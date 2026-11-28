from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.models import Component, PricePoint, Rule
from app.api.deps import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])


class ComponentAdminCreate(BaseModel):
    category_id: int
    name: str
    specs_json: Dict[str, Any] = {}
    typical_use: str
    low_inr: float
    high_inr: float


class ComponentAdminUpdate(BaseModel):
    name: Optional[str] = None
    specs_json: Optional[Dict[str, Any]] = None
    typical_use: Optional[str] = None
    active: Optional[bool] = None
    low_inr: Optional[float] = None
    high_inr: Optional[float] = None


class RuleAdminCreate(BaseModel):
    id: str
    area: str
    text: str
    severity: str
    version: int = 1


@router.get("/components")
def list_admin_components(db: Session = Depends(get_db)):
    comps = db.query(Component, PricePoint).outerjoin(PricePoint, Component.id == PricePoint.component_id).all()
    results = []
    for c, p in comps:
        results.append({
            "id": c.id,
            "category_id": c.category_id,
            "name": c.name,
            "specs_json": c.specs_json,
            "typical_use": c.typical_use,
            "active": c.active,
            "low_inr": p.low_inr if p else 0,
            "high_inr": p.high_inr if p else 0,
            "price_verified": p.price_verified if p else False,
        })
    return results


@router.post("/components")
def create_admin_component(data: ComponentAdminCreate, db: Session = Depends(get_db)):
    comp = Component(
        category_id=data.category_id,
        name=data.name,
        specs_json=data.specs_json,
        typical_use=data.typical_use,
        active=True,
    )
    db.add(comp)
    db.flush()

    price = PricePoint(
        component_id=comp.id,
        low_inr=data.low_inr,
        high_inr=data.high_inr,
        price_verified=False,
    )
    db.add(price)
    db.commit()
    return {"status": "created", "component_id": comp.id}


@router.get("/rules")
def list_admin_rules(db: Session = Depends(get_db)):
    rules = db.query(Rule).all()
    return [{"id": r.id, "area": r.area, "text": r.text, "severity": r.severity, "version": r.version} for r in rules]


@router.post("/rules")
def create_admin_rule(data: RuleAdminCreate, db: Session = Depends(get_db)):
    rule = Rule(
        id=data.id,
        area=data.area,
        text=data.text,
        severity=data.severity,
        version=data.version,
    )
    db.add(rule)
    db.commit()
    return {"status": "created", "rule_id": rule.id}
