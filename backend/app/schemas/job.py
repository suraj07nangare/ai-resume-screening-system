import uuid
from datetime import datetime

from pydantic import BaseModel


class JobCreate(BaseModel):
    title: str
    raw_description: str


class JobRead(BaseModel):
    id: uuid.UUID
    title: str
    raw_description: str
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    responsibilities: list[str] = []
    qualifications: list[str] = []
    minimum_experience_years: float | None = None
    education_requirement: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
