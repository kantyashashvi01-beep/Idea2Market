import json
import logging
import time
from typing import Type, TypeVar, Literal
from pydantic import BaseModel, ValidationError
from app.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    def __init__(self):
        if not settings.LLM_API_KEY:
            raise ValueError("GEMINI_API_KEY / LLM_API_KEY is not set.")
        try:
            from google import genai
            from google.genai import types
            self.client = genai.Client(api_key=settings.LLM_API_KEY)
            self.types = types
        except ImportError:
            raise ImportError("google-genai package is not installed. Please install requirements.txt")

    def generate_json(
        self,
        *,
        system: str,
        user: str,
        schema: Type[T],
        model_role: Literal["strong", "fast"] = "fast",
    ) -> T:
        model_name = settings.LLM_MODEL_STRONG if model_role == "strong" else settings.LLM_MODEL_FAST
        logger.info("Calling Gemini model=%s for schema=%s", model_name, schema.__name__)

        start_time = time.time()
        prompt_content = f"System Instructions:\n{system}\n\nUser Request:\n{user}"

        for attempt in range(2):
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt_content,
                    config=self.types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                        temperature=0.2,
                    ),
                )
                raw_text = response.text or "{}"
                latency = time.time() - start_time
                logger.info("Gemini response received in %.2fs (attempt %d)", latency, attempt + 1)

                data = json.loads(raw_text)
                return schema.model_validate(data)

            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning("Validation failed on attempt %d: %s", attempt + 1, str(e))
                if attempt == 0:
                    prompt_content += f"\n\nERROR IN PREVIOUS OUTPUT:\n{str(e)}\nEnsure response matches the required JSON schema strictly."
                else:
                    raise RuntimeError(f"Gemini output failed schema validation after retry: {str(e)}")
            except Exception as e:
                logger.error("Gemini API call failed: %s", str(e))
                raise RuntimeError(f"Gemini API error: {str(e)}")

        raise RuntimeError("Failed to generate valid structured response from Gemini.")
