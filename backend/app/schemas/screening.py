import uuid
from datetime import datetime

from pydantic import BaseModel


class ScreeningCreate(BaseModel):
    candidate_id: uuid.UUID
    job_id: uuid.UUID


class SkillMatchDetail(BaseModel):
    skill: str
    match_type: str
    match_score: float
    explanation: str | None = None


class ScreeningResult(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    overall_score: float
    skills_score: float
    experience_score: float
    education_score: float
    other_score: float
    matched_skills: list[str]
    partial_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    gaps: list[str]
    ai_summary: str | None
    explanation: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RankingEntry(BaseModel):
    rank: int
    candidate_id: uuid.UUID
    candidate_name: str
    overall_score: float
    skills_score: float
    experience_score: float
    matched_skills: list[str]
    missing_skills: list[str]


class RankingResponse(BaseModel):
    job_id: uuid.UUID
    job_title: str
    rankings: list[RankingEntry]
