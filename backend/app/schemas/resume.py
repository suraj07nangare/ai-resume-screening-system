import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ExtractedProject(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)


class ExtractedEducation(BaseModel):
    degree: str | None = None
    institution: str | None = None
    year: str | None = None


class ExtractedExperience(BaseModel):
    title: str | None = None
    company: str | None = None
    start_date: str | None = Field(description="Format: YYYY-MM")
    end_date: str | None = Field(description="Format: YYYY-MM or 'Present'")
    description: str | None = None


class ResumeExtraction(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    total_experience_years: float | None = None
    experience: list[ExtractedExperience] = Field(default_factory=list)
    education: list[ExtractedEducation] = Field(default_factory=list)
    education_summary: str | None = None
    projects: list[ExtractedProject] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    summary: str | None = None


class ResumeFileRead(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID | None
    filename: str
    file_type: str
    file_size: int
    extraction_status: str
    extraction_method: str | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeUploadResponse(BaseModel):
    resume_file: ResumeFileRead
    candidate: "CandidateRead | None" = None


from app.schemas.candidate import CandidateRead  # noqa: E402

ResumeUploadResponse.model_rebuild()
