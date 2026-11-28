from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str


class UserOut(BaseModel):
    id: str
    email: str
    role: str


# Project Schemas
class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    idea_text: str = Field(..., min_length=10, max_length=5000)
    domain: Optional[str] = "agricultural_robotics"


class ClarificationAnswerItem(BaseModel):
    question_id: str
    answer: str


class ClarificationSubmitRequest(BaseModel):
    answers: List[ClarificationAnswerItem]


class RequirementOut(BaseModel):
    id: str
    kind: str
    text: str
    priority: str
    source_type: str


class SubsystemOut(BaseModel):
    id: str
    name: str
    purpose: str
    maps_to_requirement_ids: List[str] = []


class InterfaceOut(BaseModel):
    id: str
    from_subsystem: str
    to_subsystem: str
    description: str


class BOMItemOut(BaseModel):
    id: str
    component_id: int
    name: str
    quantity: int
    role_in_design: str
    confidence: str
    source_type: str
    low_inr: float
    high_inr: float
    price_verified: bool
    checked_on: Optional[str] = None
    source_note: str


class BOMItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=1, le=100)
    component_id: Optional[int] = None
    role_in_design: Optional[str] = None


class AllowanceItem(BaseModel):
    name: str
    label: str
    percent: float


class AllowancesUpdateRequest(BaseModel):
    allowances: List[AllowanceItem]


class RiskOut(BaseModel):
    id: str
    title: str
    severity: str
    reason: str
    needs_expert: bool


class RoadmapStageOut(BaseModel):
    id: str
    position: int
    title: str
    deliverable: str
    duration_note: str


class RuleFindingOut(BaseModel):
    id: str
    rule_id: str
    status: str
    note: str


class JobOut(BaseModel):
    id: str
    project_id: str
    status: str
    stage: str
    progress_percent: int
    error_message: Optional[str] = None


class FacilityOut(BaseModel):
    id: int
    name: str
    facility_type: str
    city: str
    url: str
    notes: str


class ProjectOut(BaseModel):
    id: str
    title: str
    domain: str
    status: str
    safety_flag: bool
    created_at: str
    updated_at: str


class ProjectDetailOut(BaseModel):
    project: ProjectOut
    idea_text: str
    clarifications: List[Dict[str, Any]]
    requirements: List[RequirementOut]
    subsystems: List[SubsystemOut]
    interfaces: List[InterfaceOut]
    bom: Dict[str, Any]
    risks: List[RiskOut]
    roadmap: List[RoadmapStageOut]
    rule_findings: List[RuleFindingOut]
    safety_warning: Optional[str] = None
    disclaimer: str
