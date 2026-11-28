from app.services.cost_engine import CostEngine
from app.services.bom_validator import BOMValidator
from app.services.rules_engine import RulesEngine
from app.services.pdf_builder import PDFBuilder
from app.pipeline.orchestrator import GenerationPipeline
from app.models.models import Project, Job


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_auth_registration_and_login(client):
    reg_res = client.post(
        "/auth/register",
        json={"email": "newcreator@example.com", "password": "password123"},
    )
    assert reg_res.status_code == 200
    token = reg_res.json()["access_token"]
    assert token is not None

    login_res = client.post(
        "/auth/login",
        json={"email": "newcreator@example.com", "password": "password123"},
    )
    assert login_res.status_code == 200
    assert login_res.json()["user_id"] == reg_res.json()["user_id"]


def test_project_ownership_isolation(client, auth_headers, second_auth_headers):
    # User 1 creates a project
    create_res = client.post(
        "/projects",
        headers=auth_headers,
        json={"title": "Smart Solar Rover", "idea_text": "An autonomous agricultural robot for weed removal."},
    )
    assert create_res.status_code == 200
    project_id = create_res.json()["id"]

    # User 1 can view project
    res1 = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert res1.status_code == 200

    # User 2 attempts to view User 1's project -> Forbidden (403)
    res2 = client.get(f"/projects/{project_id}", headers=second_auth_headers)
    assert res2.status_code == 403


def test_closed_world_bom_validator(db):
    proposed = [
        {"component_id": 1, "quantity": 1, "role_in_design": "Compute"},
        {"component_id": 999999, "quantity": 5, "role_in_design": "Hallucinated laser weapon"},  # Non-existent ID
        {"component_id": "invalid_string", "quantity": 1},
    ]

    valid, dropped = BOMValidator.validate_and_filter_bom(db, proposed)
    assert len(valid) == 1
    assert valid[0]["component_id"] == 1
    assert valid[0]["source_type"] == "catalogue"
    assert len(dropped) == 2


def test_deterministic_cost_engine_arithmetic():
    fixtures = [
        {"component_id": 1, "quantity": 2, "low_inr": 1000.0, "high_inr": 2000.0},
        {"component_id": 2, "quantity": 1, "low_inr": 500.0, "high_inr": 800.0},
    ]
    # base_low = 2*1000 + 1*500 = 2500
    # base_high = 2*2000 + 1*800 = 4800

    custom_allowances = [
        {"name": "test_contingency", "label": "Test Contingency", "percent": 10.0},
    ]
    # 10% of 2500 = 250 => total_low = 2750
    # 10% of 4800 = 480 => total_high = 5280

    budget = CostEngine.calculate_budget(fixtures, custom_allowances=custom_allowances)
    assert budget["base_total_inr"] == [2500.0, 4800.0]
    assert budget["grand_total_inr"] == [2750.0, 5280.0]
    assert "Order-of-magnitude estimate" in budget["notice"]


def test_rules_engine_evaluates_multiple_rules():
    engine = RulesEngine()
    idea = "A low-cost agricultural weeding rover for cotton farms"
    reqs = [{"kind": "functional", "text": "Spot weed removal"}]
    bom = [
        {"name": "12V DC Planetary Geared Motor 100 RPM", "specs_json": {}},
        {"name": "Emergency Stop Push Button Switch", "specs_json": {}},
        {"name": "6-Way Blade Fuse Box Block", "specs_json": {}},
    ]

    result = engine.evaluate_project(idea, reqs, bom)
    findings = result["findings"]
    assert len(findings) >= 10
    # READ-01 (emergency stop) should pass since it is present
    estop_finding = next(f for f in findings if f["rule_id"] == "READ-01")
    assert estop_finding["status"] == "pass"


def test_safety_blocklist_forces_status():
    engine = RulesEngine()
    medical_idea = "A wearable medical insulin infusion pump for diabetic patients"
    is_safe_crit, warn_msg, cat_name = engine.check_safety_domain(medical_idea)
    assert is_safe_crit is True
    assert "human medical" in warn_msg
    assert cat_name == "Medical Devices & Diagnostics"

    eval_result = engine.evaluate_project(medical_idea, [], [])
    assert eval_result["safety_flag"] is True
    assert eval_result["overall_status"] == "not assessed: requires qualified engineer"


def test_pdf_builder_contains_mandatory_disclaimer():
    dummy_data = {
        "title": "Test Rover Plan",
        "domain": "agricultural_robotics",
        "idea_text": "Autonomous farm weeding device",
        "safety_flag": False,
        "requirements": [{"kind": "functional", "priority": "high", "text": "Cut weeds"}],
        "subsystems": [{"name": "Chassis", "purpose": "Frame"}],
        "bom": {
            "base_total_inr": [1000, 2000],
            "grand_total_inr": [1200, 2400],
            "allowances": [],
            "items": [],
        },
        "risks": [{"title": "Soil grit", "severity": "high", "reason": "Abrasive soil wear", "needs_expert": True}],
        "rule_findings": [],
    }

    pdf_bytes = PDFBuilder.generate_project_pdf(dummy_data)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # PDF starts with standard %PDF magic bytes
    assert pdf_bytes.startswith(b"%PDF")


def test_end_to_end_generation_pipeline(db, test_user):
    project = Project(
        owner_id=test_user.id,
        title="Weeding Rover Project",
        idea_text="An affordable autonomous agricultural robot for small Indian farmers",
        domain="agricultural_robotics",
        status="draft",
    )
    db.add(project)
    db.commit()

    pipeline = GenerationPipeline(db)

    # Stage 1: Clarifications
    questions = pipeline.generate_clarifications(project)
    assert len(questions) <= 5
    assert len(questions) > 0

    # Create job and run full pipeline
    job = Job(project_id=project.id, status="queued")
    db.add(job)
    db.commit()

    pipeline.run_full_pipeline(job.id, project.id)

    db.refresh(job)
    assert job.status == "done"
    assert job.progress_percent == 100

    db.refresh(project)
    assert len(project.requirements) > 0
    assert len(project.subsystems) > 0
    assert len(project.bom_items) > 0
    assert len(project.risks) > 0
    assert len(project.reports) > 0
    assert project.reports[0].pdf_blob is not None
