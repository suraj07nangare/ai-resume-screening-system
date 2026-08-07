import uuid

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.db.models.base import GUID, new_uuid
from sqlalchemy import DateTime, func


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("normalized_name", name="uq_skill_normalized_name"),)

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    candidate_skills: Mapped[list["CandidateSkill"]] = relationship(back_populates="skill")
