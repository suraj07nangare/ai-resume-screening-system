import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.skill import Skill
from app.utils.normalization import normalize_skill


class SkillRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_or_create(self, name: str) -> Skill:
        normalized = normalize_skill(name)
        existing = self._db.execute(select(Skill).where(Skill.normalized_name == normalized)).scalar_one_or_none()
        if existing:
            return existing
        skill = Skill(name=name.strip(), normalized_name=normalized)
        self._db.add(skill)
        self._db.flush()
        return skill

    def get_by_ids(self, skill_ids: list[uuid.UUID]) -> list[Skill]:
        return list(self._db.execute(select(Skill).where(Skill.id.in_(skill_ids))).scalars())
