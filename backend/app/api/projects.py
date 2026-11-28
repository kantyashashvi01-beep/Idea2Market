from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response, status
from sqlalchemy.orm import Session
from app.db import get_db, SessionLocal
from app.models.models import (
    User,
    Project,
    Clarification,
    Requirement,
    BOMItem,
    PricePoint,
    Report,
    Job,
)
from app.schemas.api_schemas import (
    ProjectCreate,
    ProjectOut,
    ProjectDetailOut,
    ClarificationSubmitRequest,
    BOMItemUpdate,
    AllowancesUpdateRequest,
    RequirementOut,
    SubsystemOut,
    InterfaceOut,
    RiskOut,
    RoadmapStageOut,
    RuleFindingOut,
)
from app.api.deps import get_current_user
from app.pipeline.orchestrator import GenerationPipeline
from app.services.cost_engine import CostEngine
from app.services.bom_validator import BOMValidator
from app.services.pdf_builder import PDFBuilder, DISCLAIMER_TEXT

router = APIRouter(prefix="/projects", tags=["Projects"])


def run_pipeline_task(job_id: str, project_id: str):
    db = SessionLocal()
    try:
        pipeline = GenerationPipeline(db)
        pipeline.run_full_pipeline(job_id, project_id)
    finally:
        db.close()


def get_user_project(project_id: str, current_user: User, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Project not found."}},
        )
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "forbidden", "message": "Access denied to this project."}},
        )
    return project


@router.post("", response_model=ProjectOut)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(
        owner_id=current_user.id,
        title=data.title.strip(),
        idea_text=data.idea_text.strip(),
        domain=data.domain or "agricultural_robotics",
        status="draft",
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return ProjectOut(
        id=project.id,
        title=project.title,
        domain=project.domain,
        status=project.status,
        safety_flag=project.safety_flag,
        created_at=str(project.created_at),
        updated_at=str(project.updated_at),
    )


@router.get("", response_model=List[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = (
        db.query(Project)
        .filter(Project.owner_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return [
        ProjectOut(
            id=p.id,
            title=p.title,
            domain=p.domain,
            status=p.status,
            safety_flag=p.safety_flag,
            created_at=str(p.created_at),
            updated_at=str(p.updated_at),
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectDetailOut)
def get_project_detail(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)

    # Compile BOM items with price points
    bom_records = (
        db.query(BOMItem, PricePoint)
        .outerjoin(PricePoint, BOMItem.component_id == PricePoint.component_id)
        .filter(BOMItem.project_id == project.id)
        .all()
    )

    bom_item_dicts = []
    for bi, pp in bom_records:
        bom_item_dicts.append({
            "id": bi.id,
            "component_id": bi.component_id,
            "name": bi.component.name if bi.component else f"Component {bi.component_id}",
            "quantity": bi.quantity,
            "role_in_design": bi.role_in_design,
            "confidence": bi.confidence,
            "source_type": bi.source_type,
            "low_inr": pp.low_inr if pp else 0.0,
            "high_inr": pp.high_inr if pp else 0.0,
            "price_verified": pp.price_verified if pp else False,
            "checked_on": str(pp.checked_on) if (pp and pp.checked_on) else None,
            "source_note": pp.source_note if pp else "placeholder",
        })

    budget = CostEngine.calculate_budget(bom_item_dicts)

    clarifications = [
        {"id": c.id, "question": c.question, "answer": c.answer, "position": c.position}
        for c in project.clarifications
    ]

    requirements = [
        RequirementOut(
            id=r.id,
            kind=r.kind,
            text=r.text,
            priority=r.priority,
            source_type=r.source_type,
        )
        for r in project.requirements
    ]

    subsystems = [
        SubsystemOut(
            id=s.id,
            name=s.name,
            purpose=s.purpose,
            maps_to_requirement_ids=s.maps_to_requirement_ids or [],
        )
        for s in project.subsystems
    ]

    interfaces = [
        InterfaceOut(
            id=i.id,
            from_subsystem=i.from_subsystem,
            to_subsystem=i.to_subsystem,
            description=i.description,
        )
        for i in project.interfaces
    ]

    risks = [
        RiskOut(
            id=r.id,
            title=r.title,
            severity=r.severity,
            reason=r.reason,
            needs_expert=r.needs_expert,
        )
        for r in project.risks
    ]

    roadmap = [
        RoadmapStageOut(
            id=rm.id,
            position=rm.position,
            title=rm.title,
            deliverable=rm.deliverable,
            duration_note=rm.duration_note,
        )
        for rm in project.roadmap_stages
    ]

    findings = [
        RuleFindingOut(
            id=rf.id,
            rule_id=rf.rule_id,
            status=rf.status,
            note=rf.note,
        )
        for rf in project.rule_findings
    ]

    safety_warning = None
    if project.safety_flag:
        pipeline = GenerationPipeline(db)
        _, warning, _ = pipeline.rules_engine.check_safety_domain(project.idea_text)
        safety_warning = warning or "Safety-critical domain detected. Expert engineer review is required."

    return ProjectDetailOut(
        project=ProjectOut(
            id=project.id,
            title=project.title,
            domain=project.domain,
            status=project.status,
            safety_flag=project.safety_flag,
            created_at=str(project.created_at),
            updated_at=str(project.updated_at),
        ),
        idea_text=project.idea_text,
        clarifications=clarifications,
        requirements=requirements,
        subsystems=subsystems,
        interfaces=interfaces,
        bom=budget,
        risks=risks,
        roadmap=roadmap,
        rule_findings=findings,
        safety_warning=safety_warning,
        disclaimer=DISCLAIMER_TEXT,
    )


@router.post("/{project_id}/clarify")
def generate_clarifications(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)
    pipeline = GenerationPipeline(db)
    questions = pipeline.generate_clarifications(project)

    # Clear previous clarifications
    db.query(Clarification).filter(Clarification.project_id == project.id).delete()
    saved = []
    for idx, q in enumerate(questions):
        c = Clarification(
            project_id=project.id,
            question=q["question"],
            position=idx + 1,
        )
        db.add(c)
        saved.append(c)

    db.commit()
    return [{"id": c.id, "question": c.question, "position": c.position} for c in saved]


@router.post("/{project_id}/answers")
def submit_clarification_answers(
    project_id: str,
    req: ClarificationSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)
    for ans in req.answers:
        c = db.query(Clarification).filter(
            Clarification.id == ans.question_id,
            Clarification.project_id == project.id,
        ).first()
        if c:
            c.answer = ans.answer.strip()

    db.commit()
    return {"status": "answers_recorded"}


@router.post("/{project_id}/generate")
def generate_project_pipeline(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)

    job = Job(
        project_id=project.id,
        status="queued",
        stage="init",
        progress_percent=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(run_pipeline_task, job.id, project.id)

    return {"job_id": job.id, "status": "queued"}


@router.patch("/{project_id}/requirements/{req_id}")
def update_requirement(
    project_id: str,
    req_id: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)
    req = db.query(Requirement).filter(
        Requirement.id == req_id,
        Requirement.project_id == project.id,
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Requirement not found."}})

    if "text" in data:
        req.text = str(data["text"]).strip()
    if "priority" in data:
        req.priority = str(data["priority"]).lower()
    if "kind" in data:
        req.kind = str(data["kind"]).lower()

    db.commit()
    return {"status": "updated", "id": req.id}


@router.get("/{project_id}/bom")
def get_bom(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)
    bom_records = (
        db.query(BOMItem, PricePoint)
        .outerjoin(PricePoint, BOMItem.component_id == PricePoint.component_id)
        .filter(BOMItem.project_id == project.id)
        .all()
    )

    bom_item_dicts = []
    for bi, pp in bom_records:
        bom_item_dicts.append({
            "id": bi.id,
            "component_id": bi.component_id,
            "name": bi.component.name if bi.component else f"Component {bi.component_id}",
            "quantity": bi.quantity,
            "role_in_design": bi.role_in_design,
            "confidence": bi.confidence,
            "source_type": bi.source_type,
            "low_inr": pp.low_inr if pp else 0.0,
            "high_inr": pp.high_inr if pp else 0.0,
            "price_verified": pp.price_verified if pp else False,
            "checked_on": str(pp.checked_on) if (pp and pp.checked_on) else None,
            "source_note": pp.source_note if pp else "placeholder",
        })

    budget = CostEngine.calculate_budget(bom_item_dicts)
    return budget


@router.patch("/{project_id}/bom/{item_id}")
def update_bom_item(
    project_id: str,
    item_id: str,
    data: BOMItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)
    item = db.query(BOMItem).filter(BOMItem.id == item_id, BOMItem.project_id == project.id).first()
    if not item:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "BOM item not found."}})

    if data.quantity is not None:
        item.quantity = max(1, min(100, data.quantity))

    if data.component_id is not None:
        # Validate that new component ID exists in closed-world catalogue
        valid, dropped = BOMValidator.validate_and_filter_bom(
            db, [{"component_id": data.component_id, "quantity": item.quantity, "role_in_design": item.role_in_design}]
        )
        if not valid:
            raise HTTPException(
                status_code=400,
                detail={"error": {"code": "invalid_component", "message": f"Component ID {data.component_id} does not exist in catalogue."}},
            )
        item.component_id = data.component_id

    if data.role_in_design is not None:
        item.role_in_design = data.role_in_design.strip()

    db.commit()

    # Return recalculated BOM
    return get_bom(project_id, db, current_user)


@router.patch("/{project_id}/allowances")
def update_allowances(
    project_id: str,
    data: AllowancesUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)
    bom_records = (
        db.query(BOMItem, PricePoint)
        .outerjoin(PricePoint, BOMItem.component_id == PricePoint.component_id)
        .filter(BOMItem.project_id == project.id)
        .all()
    )

    bom_item_dicts = []
    for bi, pp in bom_records:
        bom_item_dicts.append({
            "id": bi.id,
            "component_id": bi.component_id,
            "name": bi.component.name if bi.component else f"Component {bi.component_id}",
            "quantity": bi.quantity,
            "role_in_design": bi.role_in_design,
            "confidence": bi.confidence,
            "source_type": bi.source_type,
            "low_inr": pp.low_inr if pp else 0.0,
            "high_inr": pp.high_inr if pp else 0.0,
            "price_verified": pp.price_verified if pp else False,
            "checked_on": str(pp.checked_on) if (pp and pp.checked_on) else None,
            "source_note": pp.source_note if pp else "placeholder",
        })

    custom_allowances = [a.model_dump() for a in data.allowances]
    budget = CostEngine.calculate_budget(bom_item_dicts, custom_allowances=custom_allowances)
    return budget


@router.get("/{project_id}/risks", response_model=List[RiskOut])
def get_risks(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)
    return [
        RiskOut(
            id=r.id,
            title=r.title,
            severity=r.severity,
            reason=r.reason,
            needs_expert=r.needs_expert,
        )
        for r in project.risks
    ]


@router.get("/{project_id}/readiness", response_model=List[RuleFindingOut])
def get_readiness(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)
    return [
        RuleFindingOut(
            id=rf.id,
            rule_id=rf.rule_id,
            status=rf.status,
            note=rf.note,
        )
        for rf in project.rule_findings
    ]


@router.post("/{project_id}/report")
def build_report(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)
    detail = get_project_detail(project_id, db, current_user)

    report_data = {
        "title": project.title,
        "domain": project.domain,
        "idea_text": project.idea_text,
        "safety_flag": project.safety_flag,
        "safety_warning": detail.safety_warning,
        "requirements": [r.model_dump() for r in detail.requirements],
        "subsystems": [s.model_dump() for s in detail.subsystems],
        "bom": detail.bom,
        "risks": [r.model_dump() for r in detail.risks],
        "rule_findings": [rf.model_dump() for rf in detail.rule_findings],
        "disclaimer": DISCLAIMER_TEXT,
    }

    pdf_bytes = PDFBuilder.generate_project_pdf(report_data)

    db.query(Report).filter(Report.project_id == project.id).delete()
    report = Report(
        project_id=project.id,
        version=1,
        pdf_blob=pdf_bytes,
        status="ai_draft",
    )
    db.add(report)
    db.commit()

    return {"status": "generated", "version": 1}


@router.get("/{project_id}/report")
def download_report(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_user_project(project_id, current_user, db)
    report = db.query(Report).filter(Report.project_id == project.id).first()
    if not report or not report.pdf_blob:
        # Build if not already built
        build_report(project_id, db, current_user)
        report = db.query(Report).filter(Report.project_id == project.id).first()

    return Response(
        content=report.pdf_blob,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="idea2market_{project.title.lower().replace(" ", "_")}.pdf"'
        },
    )
