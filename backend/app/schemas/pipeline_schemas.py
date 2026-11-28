from typing import List, Literal
from pydantic import BaseModel, Field


# Stage 1: Clarification Schema
class ClarificationQuestionItem(BaseModel):
    question: str = Field(..., description="A specific clarifying technical/operational question")
    context_reason: str = Field(..., description="Why this information is needed for architecture or BOM")


class ClarificationQuestionsOutput(BaseModel):
    questions: List[ClarificationQuestionItem] = Field(
        ...,
        max_length=5,
        description="Up to 5 clarifying questions for the hardware creator",
    )


# Stage 2: Requirements Schema
class RequirementGeneratedItem(BaseModel):
    kind: Literal["functional", "constraint", "assumption"]
    text: str = Field(..., description="Clear requirement statement")
    priority: Literal["high", "medium", "low"] = "medium"
    source_type: Literal["model_estimate", "catalogue", "rule"] = "model_estimate"


class RequirementsOutput(BaseModel):
    problem_restatement: str
    target_users: str
    requirements: List[RequirementGeneratedItem]


# Stage 3: Architecture Schema
class SubsystemGeneratedItem(BaseModel):
    name: str = Field(..., description="Name of the subsystem e.g. Drivetrain, Vision Processing")
    purpose: str = Field(..., description="Core responsibility of this subsystem")
    interfaces_with: List[str] = Field(default_factory=list)


class InterfaceGeneratedItem(BaseModel):
    from_subsystem: str
    to_subsystem: str
    description: str = Field(..., description="Data, power, or mechanical interface description")


class ArchitectureOutput(BaseModel):
    subsystems: List[SubsystemGeneratedItem]
    interfaces: List[InterfaceGeneratedItem]


# Stage 5: Proposed BOM Schema
class ProposedBOMItem(BaseModel):
    component_id: int = Field(..., description="ID matching a component in the provided catalogue")
    quantity: int = Field(default=1, ge=1, le=100)
    role_in_design: str = Field(..., description="Function of this component in the design")
    confidence: Literal["high", "medium", "low"] = "medium"


class ProposedBOMOutput(BaseModel):
    items: List[ProposedBOMItem]
    assumptions_note: str = Field(default="", description="Explicit notes or unknown flags")


# Stage 8: Roadmap & Risks Schema
class RoadmapStageGeneratedItem(BaseModel):
    position: int
    title: str
    deliverable: str
    duration_note: str


class RiskGeneratedItem(BaseModel):
    title: str
    severity: Literal["high", "medium", "low"]
    reason: str = Field(..., description="Mandatory detailed explanation of the failure mode or risk")
    needs_expert: bool = Field(default=True, description="Flag indicating human engineer review is required")


class RoadmapAndRisksOutput(BaseModel):
    stages: List[RoadmapStageGeneratedItem]
    risks: List[RiskGeneratedItem]
