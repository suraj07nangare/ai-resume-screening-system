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

    notifications_enabled: bool = False
    auto_update_candidate_status: bool = True

    email_provider: str = "none"

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True

    sendgrid_api_key: str | None = None
    sendgrid_from_email: str | None = None

    shortlist_score_threshold: float = 70.0
    reject_score_threshold: float = 40.0
    schedule_link_score_threshold: float = 80.0

    calcom_scheduling_url: str | None = None
    company_name: str = "Our Company"


@lru_cache
def get_settings() -> Settings:
    return Settings()
