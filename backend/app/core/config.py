from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./resume_screener.db"

    llm_provider: str = "mock"
    llm_model: str = "gpt-4o-mini"

    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    anthropic_api_key: str | None = None
    groq_api_key: str | None = None
    openrouter_api_key: str | None = None
    llm_base_url: str | None = None

    max_upload_size_mb: int = 10

    ocr_min_text_chars: int = 50

    skills_weight: float = 0.40
    experience_weight: float = 0.30
    education_weight: float = 0.20
    other_weight: float = 0.10

    cors_origins: str = "*"


@lru_cache
def get_settings() -> Settings:
    return Settings()
