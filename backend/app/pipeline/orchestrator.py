import os
import logging
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.models import (
    Project,
    Job,
    Requirement,
    Subsystem,
    Interface,
    BOMItem,
    Risk,
    RoadmapStage,
    RuleFinding,
    Report,
    ProjectVersion,
    Component,
    PricePoint,
)
from app.llm.factory import get_llm_client
from app.schemas.pipeline_schemas import (
    ClarificationQuestionsOutput,
    RequirementsOutput,
    ArchitectureOutput,
    ProposedBOMOutput,
    RoadmapAndRisksOutput,
)
from app.services.bom_validator import BOMValidator
from app.services.cost_engine import CostEngine
from app.services.rules_engine import RulesEngine
from app.services.pdf_builder import PDFBuilder, DISCLAIMER_TEXT

logger = logging.getLogger(__name__)


def load_prompt(filename: str) -> str:
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "prompts", filename))
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


class GenerationPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm_client()
        self.rules_engine = RulesEngine()

    def generate_clarifications(self, project: Project) -> List[Dict[str, str]]:
        system_prompt = load_prompt("stage_1_clarify.md")
        user_prompt = f"Product Idea: {project.idea_text}\nDomain: {project.domain}"
        output = self.llm.generate_json(
            system=system_prompt,
            user=user_prompt,
            schema=ClarificationQuestionsOutput,
            model_role="fast",
        )
        return [{"question": q.question, "context_reason": q.context_reason} for q in output.questions]

    def run_full_pipeline(self, job_id: str, project_id: str) -> None:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        project = self.db.query(Project).filter(Project.id == project_id).first()

        if not job or not project:
            logger.error("Job %s or Project %s not found", job_id, project_id)
            return

        try:
            job.status = "running"
            job.stage = "requirements"
            job.progress_percent = 10
            self.db.commit()

            # Format answers context
            qa_context = ""
            for c in project.clarifications:
                if c.answer:
                    qa_context += f"\nQ: {c.question}\nA: {c.answer}\n"

            # ----------------------------------------------------
            # Stage 2: Requirements
            # ----------------------------------------------------
            req_system = load_prompt("stage_2_requirements.md")
            req_user = f"Idea Description: {project.idea_text}\nUser Q&A:\n{qa_context}"
            req_output: RequirementsOutput = self.llm.generate_json(
                system=req_system,
                user=req_user,
                schema=RequirementsOutput,
                model_role="strong",
            )

            # Persist requirements
            self.db.query(Requirement).filter(Requirement.project_id == project.id).delete()
            for r in req_output.requirements:
                db_req = Requirement(
                    project_id=project.id,
                    kind=r.kind,
                    text=r.text,
                    priority=r.priority,
                    source_type=r.source_type,
                )
                self.db.add(db_req)

            job.stage = "architecture"
            job.progress_percent = 30
            self.db.commit()

            # ----------------------------------------------------
            # Stage 3: Architecture
            # ----------------------------------------------------
            arch_system = load_prompt("stage_3_architecture.md")
            req_summary = "\n".join([f"- [{r.kind}] {r.text}" for r in req_output.requirements])
            arch_user = f"Product Requirements:\n{req_summary}\n\nConcept:\n{project.idea_text}"
            arch_output: ArchitectureOutput = self.llm.generate_json(
                system=arch_system,
                user=arch_user,
                schema=ArchitectureOutput,
                model_role="strong",
            )

            # Persist architecture
            self.db.query(Subsystem).filter(Subsystem.project_id == project.id).delete()
            self.db.query(Interface).filter(Interface.project_id == project.id).delete()
            for s in arch_output.subsystems:
                db_sub = Subsystem(
                    project_id=project.id,
                    name=s.name,
                    purpose=s.purpose,
                    maps_to_requirement_ids=[],
                )
                self.db.add(db_sub)
            for iface in arch_output.interfaces:
                db_iface = Interface(
                    project_id=project.id,
                    from_subsystem=iface.from_subsystem,
                    to_subsystem=iface.to_subsystem,
                    description=iface.description,
                )
                self.db.add(db_iface)

            job.stage = "retrieval_and_bom"
            job.progress_percent = 50
            self.db.commit()

            # ----------------------------------------------------
            # Stage 4 & 5: Catalogue Retrieval & Closed-World BOM
            # ----------------------------------------------------
            # Retrieve active components from SQL catalogue
            catalogue_items = (
                self.db.query(Component, PricePoint)
                .outerjoin(PricePoint, Component.id == PricePoint.component_id)
                .filter(Component.active.is_(True))
                .all()
            )

            catalogue_summary = ""
            for comp, price in catalogue_items:
                catalogue_summary += f"[ID:{comp.id}] {comp.name} | Use: {comp.typical_use} | Specs: {comp.specs_json}\n"

            bom_system = load_prompt("stage_5_bom.md")
            bom_user = f"Candidate Component Catalogue:\n{catalogue_summary}\n\nSubsystems:\n{arch_user}"
            proposed_bom: ProposedBOMOutput = self.llm.generate_json(
                system=bom_system,
                user=bom_user,
                schema=ProposedBOMOutput,
                model_role="fast",
            )

            # Validate strictly against closed-world catalogue
            valid_bom, dropped = BOMValidator.validate_and_filter_bom(
                self.db,
                [item.model_dump() for item in proposed_bom.items],
            )

            # Persist valid BOM
            self.db.query(BOMItem).filter(BOMItem.project_id == project.id).delete()
            for v in valid_bom:
                db_bom = BOMItem(
                    project_id=project.id,
                    component_id=v["component_id"],
                    quantity=v["quantity"],
                    role_in_design=v["role_in_design"],
                    confidence=v["confidence"],
                    source_type="catalogue",
                )
                self.db.add(db_bom)

            job.stage = "cost_and_rules"
            job.progress_percent = 70
            self.db.commit()

            # ----------------------------------------------------
            # Stage 6: Cost Engine (Deterministic Python)
            # ----------------------------------------------------
            budget_result = CostEngine.calculate_budget(valid_bom)

            # ----------------------------------------------------
            # Stage 7: Rules Engine (DFM & Readiness & Safety)
            # ----------------------------------------------------
            rule_eval = self.rules_engine.evaluate_project(
                project.idea_text,
                [r.model_dump() for r in req_output.requirements],
                valid_bom,
            )

            project.safety_flag = rule_eval["safety_flag"]
            if rule_eval["safety_flag"]:
                project.status = "not assessed: requires qualified engineer"
            else:
                project.status = "draft"

            self.db.query(RuleFinding).filter(RuleFinding.project_id == project.id).delete()
            for f in rule_eval["findings"]:
                db_finding = RuleFinding(
                    project_id=project.id,
                    rule_id=f["rule_id"],
                    status=f["status"],
                    note=f["note"],
                )
                self.db.add(db_finding)

            job.stage = "roadmap_and_risks"
            job.progress_percent = 85
            self.db.commit()

            # ----------------------------------------------------
            # Stage 8: Roadmap & Risks
            # ----------------------------------------------------
            rr_system = load_prompt("stage_8_roadmap_risks.md")
            rr_user = f"Hardware Concept: {project.idea_text}\nSubsystems: {', '.join([s.name for s in arch_output.subsystems])}\nKey Parts: {', '.join([v['name'] for v in valid_bom[:8]])}"
            rr_output: RoadmapAndRisksOutput = self.llm.generate_json(
                system=rr_system,
                user=rr_user,
                schema=RoadmapAndRisksOutput,
                model_role="strong",
            )

            self.db.query(RoadmapStage).filter(RoadmapStage.project_id == project.id).delete()
            self.db.query(Risk).filter(Risk.project_id == project.id).delete()

            for stg in rr_output.stages:
                db_stg = RoadmapStage(
                    project_id=project.id,
                    position=stg.position,
                    title=stg.title,
                    deliverable=stg.deliverable,
                    duration_note=stg.duration_note,
                )
                self.db.add(db_stg)

            for rsk in rr_output.risks:
                db_rsk = Risk(
                    project_id=project.id,
                    title=rsk.title,
                    severity=rsk.severity,
                    reason=rsk.reason,
                    needs_expert=rsk.needs_expert,
                )
                self.db.add(db_rsk)

            job.stage = "report"
            job.progress_percent = 95
            self.db.commit()

            # ----------------------------------------------------
            # Stage 9: Report & PDF Assembly
            # ----------------------------------------------------
            report_data = {
                "title": project.title,
                "domain": project.domain,
                "idea_text": project.idea_text,
                "safety_flag": project.safety_flag,
                "safety_warning": rule_eval.get("safety_warning"),
                "requirements": [r.model_dump() for r in req_output.requirements],
                "subsystems": [s.model_dump() for s in arch_output.subsystems],
                "bom": budget_result,
                "risks": [rsk.model_dump() for rsk in rr_output.risks],
                "rule_findings": rule_eval["findings"],
                "disclaimer": DISCLAIMER_TEXT,
            }

            pdf_bytes = PDFBuilder.generate_project_pdf(report_data)

            self.db.query(Report).filter(Report.project_id == project.id).delete()
            db_report = Report(
                project_id=project.id,
                version=1,
                pdf_blob=pdf_bytes,
                status="ai_draft",
            )
            self.db.add(db_report)

            # Save snapshot in project_versions
            db_version = ProjectVersion(
                project_id=project.id,
                snapshot_json=report_data,
                model_name=self.llm.__class__.__name__,
                prompt_version="1.0",
            )
            self.db.add(db_version)

            job.status = "done"
            job.stage = "completed"
            job.progress_percent = 100
            self.db.commit()
            logger.info("Pipeline generation completed successfully for job %s", job_id)

        except Exception as e:
            logger.exception("Pipeline failed for job %s: %s", job_id, str(e))
            self.db.rollback()
            job.status = "failed"
            job.error_message = str(e)
            self.db.commit()
