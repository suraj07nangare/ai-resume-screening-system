import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.skill import SkillRead

CandidateStatus = Literal["pending", "shortlisted", "rejected"]


class CandidateBase(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    total_experience_years: float | None = None
    education_summary: str | None = None
    summary: str | None = None


class CandidateRead(CandidateBase):
    id: uuid.UUID
    status: CandidateStatus = "pending"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CandidateDetail(CandidateRead):
    skills: list[SkillRead] = []
    latest_score: float | None = None
    latest_job_title: str | None = None


class CandidateListItem(CandidateRead):
    skills: list[str] = []
    resume_status: str | None = None
    latest_score: float | None = None
    latest_job_title: str | None = None


class CandidateListResponse(BaseModel):
    items: list[CandidateListItem]
    total: int
    limit: int
    offset: int


class CandidateStatusUpdate(BaseModel):
    status: CandidateStatus
