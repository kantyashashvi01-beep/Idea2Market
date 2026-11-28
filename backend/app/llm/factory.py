from app.config import settings
from app.llm.client import LLMClient
from app.llm.fake import FakeLLMClient


def get_llm_client() -> LLMClient:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "gemini":
        from app.llm.gemini import GeminiClient
        return GeminiClient()
    elif provider == "anthropic":
        from app.llm.anthropic import AnthropicClient
        return AnthropicClient()
    elif provider == "fake":
        return FakeLLMClient()
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER}. Expected 'gemini', 'anthropic', or 'fake'.")
