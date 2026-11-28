import logging
import time
from typing import Type, TypeVar, Literal
from pydantic import BaseModel, ValidationError
from app.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class AnthropicClient:
    def __init__(self):
        if not settings.LLM_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY / LLM_API_KEY is not set.")
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=settings.LLM_API_KEY)
        except ImportError:
            raise ImportError("anthropic package is not installed. Please install requirements.txt")

    def generate_json(
        self,
        *,
        system: str,
        user: str,
        schema: Type[T],
        model_role: Literal["strong", "fast"] = "fast",
    ) -> T:
        model_name = settings.LLM_MODEL_STRONG if model_role == "strong" else settings.LLM_MODEL_FAST
        logger.info("Calling Anthropic model=%s for schema=%s", model_name, schema.__name__)

        start_time = time.time()
        tool_name = f"record_{schema.__name__.lower()}"
        tools = [
            {
                "name": tool_name,
                "description": f"Record structured data for {schema.__name__}",
                "input_schema": schema.model_json_schema(),
            }
        ]

        messages = [{"role": "user", "content": user}]

        for attempt in range(2):
            try:
                response = self.client.messages.create(
                    model=model_name,
                    max_tokens=4096,
                    system=system,
                    messages=messages,
                    tools=tools,
                    tool_choice={"type": "tool", "name": tool_name},
                )
                latency = time.time() - start_time
                logger.info("Anthropic response received in %.2fs (attempt %d)", latency, attempt + 1)

                tool_call = next((b for b in response.content if b.type == "tool_use"), None)
                if not tool_call:
                    raise ValueError("No tool call in response")

                return schema.model_validate(tool_call.input)

            except (ValidationError, Exception) as e:
                logger.warning("Anthropic output failed on attempt %d: %s", attempt + 1, str(e))
                if attempt == 0:
                    messages.append({"role": "assistant", "content": f"Failed attempt: {str(e)}"})
                    messages.append({"role": "user", "content": f"Fix the validation error: {str(e)}. Output correct schema."})
                else:
                    raise RuntimeError(f"Anthropic generation failed schema validation: {str(e)}")

        raise RuntimeError("Failed to generate valid structured response from Anthropic.")
