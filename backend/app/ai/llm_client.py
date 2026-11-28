import json
import logging
import os
from typing import Any, Dict, List, Optional, Type, TypeVar

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


class LLMClientError(Exception):
    """Base exception for LLM client failures."""


class MissingAPIKeyError(LLMClientError):
    """Raised when a required LLM API key is missing."""


class LLMAPIError(LLMClientError):
    """Raised when the upstream LLM provider returns an API or transport error."""


class LLMResponseError(LLMClientError):
    """Raised when the LLM response is empty, non-JSON, or fails schema validation."""


class OpenAILLMClient:
    """Reusable OpenAI SDK wrapper with graceful configuration and error handling."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        timeout: float = 30.0,
        client: Optional[Any] = None,
        load_env: bool = True,
    ) -> None:
        if load_env:
            load_dotenv()

        self.provider = (provider or os.getenv("LLM_PROVIDER") or "openai").strip().lower()
        resolved_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")
        self.api_key = resolved_key.strip() if resolved_key else ""
        resolved_model = model if model is not None else os.getenv("OPENAI_MODEL", "")
        self.model = resolved_model.strip() or DEFAULT_OPENAI_MODEL
        self.timeout = timeout
        self._client = client

    @property
    def is_configured(self) -> bool:
        """Return True if an injected client or non-empty API key is available."""
        return self._client is not None or bool(self.api_key)

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise MissingAPIKeyError(
                "OPENAI_API_KEY is not set. Configure it in your environment or .env file."
            )
        self._client = OpenAI(api_key=self.api_key, timeout=self.timeout)
        return self._client

    def generate_text(
        self,
        *,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send chat messages to OpenAI and return the assistant text content."""
        client = self._get_client()

        request_kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            request_kwargs["max_tokens"] = max_tokens

        try:
            response = client.chat.completions.create(**request_kwargs)
        except OpenAIError as exc:
            logger.error("OpenAI API request failed: %s", exc.__class__.__name__)
            raise LLMAPIError(f"OpenAI API error: {exc}") from exc
        except Exception as exc:
            logger.error("Unexpected LLM transport error: %s", exc.__class__.__name__)
            raise LLMAPIError(f"Unexpected error calling OpenAI API: {exc}") from exc

        choices = getattr(response, "choices", None)
        if not choices:
            raise LLMResponseError("LLM response contained no completion choices.")

        message = getattr(choices[0], "message", None)
        content = getattr(message, "content", None)
        if not content or not isinstance(content, str) or not content.strip():
            raise LLMResponseError("LLM response returned empty text content.")

        return content.strip()

    def generate_structured(
        self,
        *,
        messages: List[Dict[str, str]],
        response_model: Type[T],
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> T:
        """Request JSON output from OpenAI and validate it against a Pydantic model."""
        client = self._get_client()

        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        augmented_messages = list(messages)
        augmented_messages.append(
            {
                "role": "system",
                "content": (
                    "Respond ONLY with valid JSON matching this JSON Schema:\n"
                    f"{schema_json}"
                ),
            }
        )

        request_kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": augmented_messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        if max_tokens is not None:
            request_kwargs["max_tokens"] = max_tokens

        try:
            response = client.chat.completions.create(**request_kwargs)
        except OpenAIError as exc:
            logger.error("OpenAI structured API request failed: %s", exc.__class__.__name__)
            raise LLMAPIError(f"OpenAI API error: {exc}") from exc
        except Exception as exc:
            logger.error("Unexpected structured LLM transport error: %s", exc.__class__.__name__)
            raise LLMAPIError(f"Unexpected error calling OpenAI API: {exc}") from exc

        choices = getattr(response, "choices", None)
        if not choices:
            raise LLMResponseError("LLM response contained no completion choices.")

        message = getattr(choices[0], "message", None)
        raw_content = getattr(message, "content", None)
        if not raw_content or not isinstance(raw_content, str) or not raw_content.strip():
            raise LLMResponseError("LLM response returned empty JSON content.")

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            raise LLMResponseError(f"LLM returned invalid JSON: {exc}") from exc

        try:
            return response_model.model_validate(parsed)
        except ValidationError as exc:
            raise LLMResponseError(
                f"LLM JSON failed validation for {response_model.__name__}: {exc}"
            ) from exc
