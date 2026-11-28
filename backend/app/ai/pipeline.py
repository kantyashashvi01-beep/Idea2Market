from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.ai.llm_client import OpenAILLMClient
from app.ai.prompts import (
    build_clarification_messages,
    build_idea_understanding_messages,
    build_requirements_messages,
)
from app.schemas.idea import (
    ClarificationQuestion,
    ClarificationResult,
    IdeaInput,
    ProductRequirements,
)


class IdeaUnderstandingResult(BaseModel):
    """Structured initial understanding of a hardware product idea."""

    summary: str = Field(..., min_length=5, description="Plain-language summary of the idea.")
    user_provided_facts: List[str] = Field(
        default_factory=list,
        description="Facts explicitly provided by the user.",
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Provisional assumptions kept distinct from user facts.",
    )
    unknowns: List[str] = Field(
        default_factory=list,
        description="Technical details not yet specified by the user.",
    )


class InitialPipelineOutput(BaseModel):
    """Combined output of Member 2's modular initial AI pipeline."""

    idea: IdeaInput
    understanding: IdeaUnderstandingResult
    clarifications: List[ClarificationQuestion] = Field(..., max_length=5)
    requirements: ProductRequirements


class IdeaFoundationPipeline:
    """Modular initial AI pipeline connecting IdeaInput, prompts, OpenAI client, and schemas."""

    def __init__(self, llm_client: Optional[OpenAILLMClient] = None) -> None:
        self.llm_client = llm_client or OpenAILLMClient()

    def understand_idea(self, idea: IdeaInput) -> IdeaUnderstandingResult:
        """Analyze the raw idea and separate user-stated facts from unknowns."""
        messages = build_idea_understanding_messages(idea)
        return self.llm_client.generate_structured(
            messages=messages,
            response_model=IdeaUnderstandingResult,
        )

    def generate_clarifications(self, idea: IdeaInput) -> ClarificationResult:
        """Generate up to five high-impact clarifying questions for the idea."""
        messages = build_clarification_messages(idea)
        result = self.llm_client.generate_structured(
            messages=messages,
            response_model=ClarificationResult,
        )
        if len(result.questions) > 5:
            result = result.model_copy(update={"questions": result.questions[:5]})
        return result

    def extract_requirements(
        self,
        idea: IdeaInput,
        clarification_answers: Optional[Dict[str, str]] = None,
    ) -> ProductRequirements:
        """Extract structured ProductRequirements grounded in the idea and optional answers."""
        messages = build_requirements_messages(idea, clarification_answers=clarification_answers)
        return self.llm_client.generate_structured(
            messages=messages,
            response_model=ProductRequirements,
        )

    def run(
        self,
        idea: IdeaInput,
        clarification_answers: Optional[Dict[str, str]] = None,
    ) -> InitialPipelineOutput:
        """Execute the initial understanding, clarification, and requirements stages."""
        understanding = self.understand_idea(idea)
        clarification_result = self.generate_clarifications(idea)
        requirements = self.extract_requirements(
            idea,
            clarification_answers=clarification_answers,
        )
        return InitialPipelineOutput(
            idea=idea,
            understanding=understanding,
            clarifications=clarification_result.questions,
            requirements=requirements,
        )
