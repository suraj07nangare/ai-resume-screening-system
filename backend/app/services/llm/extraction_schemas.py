from app.schemas.resume import ResumeExtraction
from pydantic import BaseModel, Field


class JobExtraction(BaseModel):
    title: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    minimum_experience_years: float | None = None
    education_requirements: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    qualifications: list[str] = Field(default_factory=list)


__all__ = ["ResumeExtraction", "JobExtraction"]
