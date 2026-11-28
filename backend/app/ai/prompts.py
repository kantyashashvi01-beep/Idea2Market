from typing import Dict, List, Mapping, Optional

from app.schemas.idea import IdeaInput

GROUNDING_RULES = (
    "STRICT GROUNDING RULES:\n"
    "1. Separate explicit user-provided facts from any provisional assumptions.\n"
    "2. Never invent missing technical specifications, part numbers, prices, or certifications.\n"
    "3. If a detail is not provided by the user, mark it explicitly as 'unknown' or list it under unknowns/missing_details.\n"
    "4. Do not perform financial calculations or cost estimates."
)

IDEA_UNDERSTANDING_PROMPT = (
    "You are a Senior AI Hardware Product Engineer assisting a non-technical creator.\n"
    "Analyze the user's hardware product idea and summarize what the user wants to build.\n"
    "Clearly distinguish between:\n"
    "- Facts explicitly stated by the user\n"
    "- Missing technical details that remain unknown\n"
    "- Provisional assumptions (if any are necessary, label them clearly as assumptions)\n\n"
    f"{GROUNDING_RULES}"
)

CLARIFICATION_QUESTIONS_PROMPT = (
    "You are a Senior AI Hardware Product Engineer helping a non-engineer refine a hardware concept.\n"
    "Based on the submitted idea, generate up to 5 high-impact clarifying questions.\n"
    "Focus on critical missing parameters such as operating environment, power/runtime, "
    "physical payload or actuation, target scale, and safety boundaries.\n"
    "For each question, explain briefly why it matters.\n"
    "Populate user_provided_facts strictly from the user's text and list unstated details in missing_details.\n\n"
    f"{GROUNDING_RULES}"
)

PRODUCT_REQUIREMENTS_PROMPT = (
    "You are a Senior AI Hardware Product Engineer translating a hardware concept and "
    "clarification answers into structured engineering requirements.\n"
    "Extract:\n"
    "- problem_statement: concise restatement grounded in user input\n"
    "- target_users: from user input, or 'unknown' if unspecified\n"
    "- user_provided_facts: only facts explicitly stated by the user\n"
    "- functional_requirements: physical behaviors the product must perform\n"
    "- constraints: explicit operating, mechanical, electrical, or safety boundaries\n"
    "- assumptions: clearly labeled provisional assumptions, never mixed into user_provided_facts\n"
    "- unknowns: missing technical parameters left explicitly unknown rather than invented\n\n"
    f"{GROUNDING_RULES}"
)

PROMPT_TEMPLATES: Mapping[str, str] = {
    "idea_understanding": IDEA_UNDERSTANDING_PROMPT,
    "clarification_questions": CLARIFICATION_QUESTIONS_PROMPT,
    "product_requirements": PRODUCT_REQUIREMENTS_PROMPT,
}


def get_prompt_template(name: str) -> str:
    """Return a named prompt template or raise KeyError if unavailable."""
    if name not in PROMPT_TEMPLATES:
        available = ", ".join(sorted(PROMPT_TEMPLATES))
        raise KeyError(f"Unknown prompt template '{name}'. Available: {available}")
    return PROMPT_TEMPLATES[name]


def _format_idea_context(idea: IdeaInput) -> str:
    lines = [
        f"Title: {idea.title or 'unknown'}",
        f"Domain: {idea.domain}",
        f"Idea Description: {idea.idea_text}",
        f"Target Users (user-stated): {idea.target_users or 'unknown'}",
        f"User Constraints Notes: {idea.constraints_notes or 'none provided'}",
    ]
    return "\n".join(lines)


def build_idea_understanding_messages(idea: IdeaInput) -> List[Dict[str, str]]:
    """Build chat messages for initial hardware idea understanding."""
    return [
        {"role": "system", "content": get_prompt_template("idea_understanding")},
        {"role": "user", "content": _format_idea_context(idea)},
    ]


def build_clarification_messages(idea: IdeaInput) -> List[Dict[str, str]]:
    """Build chat messages for generating up to 5 clarification questions."""
    return [
        {"role": "system", "content": get_prompt_template("clarification_questions")},
        {"role": "user", "content": _format_idea_context(idea)},
    ]


def build_requirements_messages(
    idea: IdeaInput,
    clarification_answers: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    """Build chat messages for extracting structured product requirements."""
    user_sections = [_format_idea_context(idea)]
    if clarification_answers:
        qa_lines = ["Clarification Q&A (user-provided):"]
        for question, answer in clarification_answers.items():
            clean_answer = answer.strip() if answer and answer.strip() else "unknown"
            qa_lines.append(f"- Q: {question}\n  A: {clean_answer}")
        user_sections.append("\n".join(qa_lines))
    else:
        user_sections.append("Clarification Q&A: none provided")

    return [
        {"role": "system", "content": get_prompt_template("product_requirements")},
        {"role": "user", "content": "\n\n".join(user_sections)},
    ]
