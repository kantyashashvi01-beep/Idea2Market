from typing import List, Literal, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: Literal["local", "production", "test"] = "local"
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgrespassword@localhost:5432/idea2market"
    SECRET_KEY: str = "default-insecure-dev-secret-key-change-in-production-32chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    LLM_PROVIDER: Literal["gemini", "anthropic", "fake"] = "fake"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL_STRONG: str = "gemini-2.5-pro"
    LLM_MODEL_FAST: str = "gemini-2.5-flash"
    MAX_TOKENS_PER_PROJECT: int = 25000

    ADMIN_EMAIL: Optional[str] = "admin@idea2market.local"
    LOG_LEVEL: str = "info"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if not v:
            return v
        url = v.strip()
        if url.startswith("postgres://"):
            url = "postgresql+psycopg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg://"):
            url = "postgresql+psycopg://" + url[len("postgresql://"):]
        return url

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def validate_production(self) -> None:
        if self.ENV == "production":
            if "default-insecure" in self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise ValueError("In production, SECRET_KEY must be a secure random string of at least 32 characters.")
            if self.LLM_PROVIDER != "fake" and not self.LLM_API_KEY:
                raise ValueError("In production, LLM_API_KEY must be provided.")


settings = Settings()
settings.validate_production()
