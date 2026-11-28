from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


def _clean_string_list(values: List[str]) -> List[str]:
    """Strip whitespace from list entries and reject blank strings."""
    cleaned: List[str] = []
    for item in values:
        stripped = item.strip()
        if not stripped:
            raise ValueError("List items must not be empty or whitespace-only.")
        cleaned.append(stripped)
    return cleaned


class IdeaInput(BaseModel):
    """Validated user-submitted hardware product idea."""

    model_config = ConfigDict(str_strip_whitespace=True)

    idea_text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Plain-language description of the hardware product idea.",
    )
    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=200,
        description="Optional short title for the hardware concept.",
    )
    domain: str = Field(
        default="general_hardware",
        min_length=2,
        max_length=100,
        description="Target hardware domain (e.g. agricultural_robotics, consumer_iot).",
    )
    target_users: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=500,
        description="Optional intended end users stated directly by the creator.",
    )
    constraints_notes: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2000,
        description="Optional user-stated constraints such as operating environment, runtime, or size.",
    )


class ClarificationQuestion(BaseModel):
    """Single high-impact clarifying question for a non-engineer creator."""

    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Specific clarifying question needed to resolve design ambiguity.",
    )
    reason: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Why this answer matters for requirements, architecture, or safety.",
    )
    category: Literal["environment", "power", "payload", "scale", "safety", "other"] = Field(
        default="other",
        description="Engineering dimension addressed by this clarifying question.",
    )
    priority: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Relative urgency of resolving this unknown before design.",
    )


class ClarificationResult(BaseModel):
    """Structured output for the idea-understanding and clarification step."""

    model_config = ConfigDict(str_strip_whitespace=True)

    idea_summary: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Concise summary of what is understood solely from user input.",
    )
    user_provided_facts: List[str] = Field(
        default_factory=list,
        description="Facts explicitly stated by the user without extrapolation.",
    )
    missing_details: List[str] = Field(
        default_factory=list,
        description="Technical parameters missing from the user's description.",
    )
    questions: List[ClarificationQuestion] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Up to five clarifying questions targeting the highest-impact unknowns.",
    )

    @field_validator("user_provided_facts", "missing_details")
    @classmethod
    def validate_string_lists(cls, value: List[str]) -> List[str]:
        return _clean_string_list(value)


class ProductRequirements(BaseModel):
    """Structured hardware product requirements separating facts, assumptions, and unknowns."""

    model_config = ConfigDict(str_strip_whitespace=True)

    problem_statement: str = Field(
        ...,
        min_length=5,
        max_length=1500,
        description="Restatement of the user's hardware problem grounded in provided input.",
    )
    target_users: str = Field(
        default="unknown",
        min_length=2,
        max_length=500,
        description="Target end users based on user input, or 'unknown' if unspecified.",
    )
    user_provided_facts: List[str] = Field(
        default_factory=list,
        description="Facts directly stated by the user or in clarification answers.",
    )
    functional_requirements: List[str] = Field(
        default_factory=list,
        description="Core physical actions or behaviors the product must perform.",
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Explicit environmental, electrical, mechanical, or safety constraints.",
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Provisional engineering assumptions, kept separate from user-provided facts.",
    )
    unknowns: List[str] = Field(
        default_factory=list,
        description="Missing technical details left explicitly unknown rather than invented.",
    )

    @field_validator(
        "user_provided_facts",
        "functional_requirements",
        "constraints",
        "assumptions",
        "unknowns",
    )
    @classmethod
    def validate_requirement_lists(cls, value: List[str]) -> List[str]:
        return _clean_string_list(value)
