import uuid

from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.db.models.base import GUID, TimestampMixin, new_uuid


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    raw_description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    qualifications: Mapped[str | None] = mapped_column(Text, nullable=True)
    minimum_experience_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    education_requirement: Mapped[str | None] = mapped_column(String(255), nullable=True)

    scores: Mapped[list["Score"]] = relationship(back_populates="job", cascade="all, delete-orphan")
