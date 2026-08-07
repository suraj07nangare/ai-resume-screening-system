import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.db.models.base import GUID, new_uuid


class ScoreSkill(Base):
    __tablename__ = "score_skills"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    score_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("scores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    match_type: Mapped[str] = mapped_column(String(20), nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    score: Mapped["Score"] = relationship(back_populates="score_skills")
    skill: Mapped["Skill"] = relationship()
