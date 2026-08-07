import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.score import Score
from app.db.models.score_skill import ScoreSkill


class ScoreRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, score: Score) -> Score:
        self._db.add(score)
        self._db.flush()
        return score

    def add_score_skill(self, score_skill: ScoreSkill) -> None:
        self._db.add(score_skill)

    def get(self, score_id: uuid.UUID) -> Score | None:
        stmt = (
            select(Score)
            .options(selectinload(Score.score_skills).selectinload(ScoreSkill.skill))
            .where(Score.id == score_id)
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def latest_for_candidate(self, candidate_id: uuid.UUID) -> Score | None:
        stmt = (
            select(Score)
            .options(selectinload(Score.job))
            .where(Score.candidate_id == candidate_id)
            .order_by(Score.created_at.desc())
            .limit(1)
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def rankings_for_job(self, job_id: uuid.UUID) -> list[Score]:
        stmt = (
            select(Score)
            .options(selectinload(Score.score_skills).selectinload(ScoreSkill.skill), selectinload(Score.candidate))
            .where(Score.job_id == job_id)
            .order_by(Score.overall_score.desc())
        )
        return list(self._db.execute(stmt).scalars())
