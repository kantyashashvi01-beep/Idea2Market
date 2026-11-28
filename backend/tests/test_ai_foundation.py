import json
from types import SimpleNamespace
from typing import Any, Dict, List

import pytest
from openai import OpenAIError
from pydantic import ValidationError

from app.ai.llm_client import (
    LLMAPIError,
    LLMResponseError,
    MissingAPIKeyError,
    OpenAILLMClient,
)
from app.ai.pipeline import IdeaFoundationPipeline
from app.ai.prompts import (
    PROMPT_TEMPLATES,
    build_clarification_messages,
    build_idea_understanding_messages,
    build_requirements_messages,
    get_prompt_template,
)
from app.schemas.idea import (
    ClarificationQuestion,
    ClarificationResult,
    IdeaInput,
    ProductRequirements,
)


def _make_fake_openai_response(content: str) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


class _StubCompletions:
    def __init__(self, responses: List[Any]) -> None:
        self._responses = list(responses)
        self.calls: List[Dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        next_item = self._responses.pop(0)
        if isinstance(next_item, Exception):
            raise next_item
        return next_item


class _StubOpenAIClient:
    def __init__(self, responses: List[Any]) -> None:
        self.chat = SimpleNamespace(completions=_StubCompletions(responses))


# ---------------------------------------------------------------------------
# Schema Validation & Invalid/Missing Input Tests
# ---------------------------------------------------------------------------


def test_idea_input_valid():
    idea = IdeaInput(
        title="  Solar Soil Sensor  ",
        idea_text="  An outdoor solar-powered soil moisture sensor node for small farms.  ",
        domain="agricultural_iot",
        target_users="Smallholder farmers",
        constraints_notes="Must survive monsoon rain",
    )
    assert idea.title == "Solar Soil Sensor"
    assert idea.domain == "agricultural_iot"
    assert idea.target_users == "Smallholder farmers"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": "Valid Title"},
        {"idea_text": "Too short"},
        {"idea_text": "          "},
        {"idea_text": "A valid hardware idea description.", "title": "Hi"},
    ],
)
def test_idea_input_invalid_or_missing_rejected(payload: Dict[str, Any]):
    with pytest.raises(ValidationError):
        IdeaInput(**payload)


def test_clarification_question_and_max_five_limit():
    valid_q = ClarificationQuestion(
        question="What runtime per charge do you expect in the field?",
        reason="Determines battery capacity and solar panel wattage.",
        category="power",
        priority="high",
    )
    result = ClarificationResult(
        idea_summary="User wants a solar soil moisture sensor for farms.",
        user_provided_facts=["Solar-powered soil moisture sensor"],
        missing_details=["Battery runtime target"],
        questions=[valid_q] * 5,
    )
    assert len(result.questions) == 5

    with pytest.raises(ValidationError):
        ClarificationResult(
            idea_summary="User wants a solar soil moisture sensor for farms.",
            questions=[valid_q] * 6,
        )


def test_clarification_question_rejects_invalid_category():
    with pytest.raises(ValidationError):
        ClarificationQuestion(
            question="What enclosure rating is needed?",
            reason="Protects electronics from rain and dust.",
            category="invalid_category",  # type: ignore[arg-type]
        )


def test_product_requirements_validation_and_empty_item_rejection():
    reqs = ProductRequirements(
        problem_statement="Measure field soil moisture autonomously using solar energy.",
        target_users="unknown",
        user_provided_facts=["Uses solar power"],
        functional_requirements=["Sense volumetric soil moisture periodically"],
        constraints=["Outdoor deployment"],
        assumptions=["Operates in daylight regions"],
        unknowns=["Wireless telemetry range"],
    )
    assert reqs.target_users == "unknown"
    assert "Uses solar power" in reqs.user_provided_facts

    with pytest.raises(ValidationError):
        ProductRequirements(
            problem_statement="Measure field soil moisture.",
            functional_requirements=["   "],
        )


# ---------------------------------------------------------------------------
# Prompt Template Availability & Grounding Tests
# ---------------------------------------------------------------------------


def test_prompt_templates_available_and_grounded():
    expected_keys = {
        "idea_understanding",
        "clarification_questions",
        "product_requirements",
    }
    assert expected_keys.issubset(PROMPT_TEMPLATES.keys())

    for key in expected_keys:
        template = get_prompt_template(key)
        assert isinstance(template, str)
        assert len(template.strip()) > 50
        lowered = template.lower()
        assert "assumption" in lowered
        assert "unknown" in lowered
        assert "never invent" in lowered

    with pytest.raises(KeyError):
        get_prompt_template("non_existent_template")


def test_prompt_message_builders():
    idea = IdeaInput(idea_text="A battery-powered water tank level monitor for apartments.")
    understanding_msgs = build_idea_understanding_messages(idea)
    clarify_msgs = build_clarification_messages(idea)
    req_msgs = build_requirements_messages(
        idea,
        clarification_answers={"What is the tank depth?": "3 meters"},
    )

    assert len(understanding_msgs) == 2
    assert understanding_msgs[0]["role"] == "system"
    assert "water tank level monitor" in understanding_msgs[1]["content"]

    assert len(clarify_msgs) == 2
    assert clarify_msgs[0]["role"] == "system"

    assert len(req_msgs) == 2
    assert "3 meters" in req_msgs[1]["content"]


# ---------------------------------------------------------------------------
# LLM Client Missing Key, Error, and Invalid Response Handling Tests
# ---------------------------------------------------------------------------


def test_missing_api_key_handled_gracefully(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    client = OpenAILLMClient(api_key="", load_env=False)
    assert client.is_configured is False

    with pytest.raises(MissingAPIKeyError, match="OPENAI_API_KEY"):
        client.generate_text(messages=[{"role": "user", "content": "Hello"}])

    with pytest.raises(MissingAPIKeyError, match="OPENAI_API_KEY"):
        client.generate_structured(
            messages=[{"role": "user", "content": "Hello"}],
            response_model=ProductRequirements,
        )


def test_llm_client_handles_api_error_and_invalid_responses():
    api_err_client = OpenAILLMClient(
        api_key="sk-test-unused",
        client=_StubOpenAIClient([OpenAIError("Simulated outage")]),
        load_env=False,
    )
    with pytest.raises(LLMAPIError, match="OpenAI API error"):
        api_err_client.generate_text(messages=[{"role": "user", "content": "Hi"}])

    bad_json_client = OpenAILLMClient(
        api_key="sk-test-unused",
        client=_StubOpenAIClient([_make_fake_openai_response("not valid json")]),
        load_env=False,
    )
    with pytest.raises(LLMResponseError, match="invalid JSON"):
        bad_json_client.generate_structured(
            messages=[{"role": "user", "content": "Hi"}],
            response_model=ProductRequirements,
        )

    empty_client = OpenAILLMClient(
        api_key="sk-test-unused",
        client=_StubOpenAIClient([_make_fake_openai_response("   ")]),
        load_env=False,
    )
    with pytest.raises(LLMResponseError, match="empty"):
        empty_client.generate_text(messages=[{"role": "user", "content": "Hi"}])


# ---------------------------------------------------------------------------
# Modular Initial Pipeline Test (Mocked SDK, Zero Network Calls)
# ---------------------------------------------------------------------------


def test_idea_foundation_pipeline_modular_run_without_live_api():
    understanding_payload = json.dumps(
        {
            "summary": "A low-cost automated plant watering unit for indoor balconies.",
            "user_provided_facts": ["Automated plant watering for indoor balconies"],
            "assumptions": ["Assumes domestic indoor temperature range"],
            "unknowns": ["Power source", "Water reservoir capacity"],
        }
    )
    clarification_payload = json.dumps(
        {
            "idea_summary": "Automated indoor balcony plant watering device.",
            "user_provided_facts": ["Indoor balcony use"],
            "missing_details": ["Power source", "Number of plants"],
            "questions": [
                {
                    "question": "Will the unit plug into a wall outlet or run on batteries?",
                    "reason": "Determines power regulation and enclosure design.",
                    "category": "power",
                    "priority": "high",
                },
                {
                    "question": "How many plant pots should one unit water?",
                    "reason": "Determines pump capacity and valve branching.",
                    "category": "payload",
                    "priority": "high",
                },
            ],
        }
    )
    requirements_payload = json.dumps(
        {
            "problem_statement": "Automatically water indoor balcony plants without manual intervention.",
            "target_users": "Urban apartment residents",
            "user_provided_facts": ["Indoor balcony use", "2 plant pots"],
            "functional_requirements": ["Deliver metered water to two pots on schedule"],
            "constraints": ["Compact indoor footprint"],
            "assumptions": ["Freshwater reservoir refilled manually"],
            "unknowns": ["Exact daily water volume per pot"],
        }
    )

    stub_sdk = _StubOpenAIClient(
        [
            _make_fake_openai_response(understanding_payload),
            _make_fake_openai_response(clarification_payload),
            _make_fake_openai_response(requirements_payload),
        ]
    )
    llm_client = OpenAILLMClient(
        api_key="sk-test-unused",
        model="gpt-4o-mini",
        client=stub_sdk,
        load_env=False,
    )
    pipeline = IdeaFoundationPipeline(llm_client=llm_client)

    idea = IdeaInput(
        title="Balcony Plant Waterer",
        idea_text="I want a simple automated plant watering device for my indoor balcony.",
        target_users="Urban apartment residents",
    )
    output = pipeline.run(
        idea,
        clarification_answers={"How many plant pots should one unit water?": "2 plant pots"},
    )

    assert len(stub_sdk.chat.completions.calls) == 3
    assert len(output.clarifications) == 2
    assert output.requirements.target_users == "Urban apartment residents"
    assert "2 plant pots" in output.requirements.user_provided_facts
    assert "Exact daily water volume per pot" in output.requirements.unknowns
