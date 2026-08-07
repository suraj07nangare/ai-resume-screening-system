import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.models.candidate import Candidate
from app.db.models.candidate_skill import CandidateSkill
from app.db.models.skill import Skill


class CandidateRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, candidate: Candidate) -> Candidate:
        self._db.add(candidate)
        self._db.flush()
        return candidate

    def get(self, candidate_id: uuid.UUID) -> Candidate | None:
        stmt = (
            select(Candidate)
            .options(selectinload(Candidate.candidate_skills).selectinload(CandidateSkill.skill))
            .where(Candidate.id == candidate_id)
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def add_skill(self, candidate_id: uuid.UUID, skill_id: uuid.UUID, source: str = "resume") -> None:
        existing = self._db.execute(
            select(CandidateSkill).where(
                CandidateSkill.candidate_id == candidate_id, CandidateSkill.skill_id == skill_id
            )
        ).scalar_one_or_none()
        if existing:
            return
        self._db.add(CandidateSkill(candidate_id=candidate_id, skill_id=skill_id, source=source))

    def search(
        self,
        name: str | None = None,
        email: str | None = None,
        skill: str | None = None,
        min_experience: float | None = None,
        max_experience: float | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Candidate], int]:
        stmt = select(Candidate).options(
            selectinload(Candidate.candidate_skills).selectinload(CandidateSkill.skill)
        )

        if name:
            stmt = stmt.where(Candidate.name.ilike(f"%{name}%"))
        if email:
            stmt = stmt.where(Candidate.email.ilike(f"%{email}%"))
        if min_experience is not None:
            stmt = stmt.where(Candidate.total_experience_years >= min_experience)
        if max_experience is not None:
            stmt = stmt.where(Candidate.total_experience_years <= max_experience)
        if status:
            stmt = stmt.where(Candidate.status == status)
        if skill:
            stmt = stmt.join(Candidate.candidate_skills).join(CandidateSkill.skill).where(
                Skill.normalized_name.ilike(f"%{skill.lower()}%")
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self._db.execute(count_stmt).scalar_one()

        stmt = stmt.order_by(Candidate.created_at.desc()).limit(limit).offset(offset)
        candidates = list(self._db.execute(stmt).unique().scalars())
        return candidates, total

    def update_status(self, candidate: Candidate, status: str) -> Candidate:
        candidate.status = status
        self._db.add(candidate)
        self._db.flush()
        return candidate

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Candidate]:
        stmt = (
            select(Candidate)
            .options(selectinload(Candidate.candidate_skills).selectinload(CandidateSkill.skill))
            .order_by(Candidate.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self._db.execute(stmt).unique().scalars())
