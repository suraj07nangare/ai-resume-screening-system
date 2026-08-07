import uuid

from sqlalchemy.orm import Session

from app.db.repositories.candidate_repository import CandidateRepository
from app.db.repositories.score_repository import ScoreRepository
from app.db.models.candidate import Candidate


class CandidateService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._candidate_repo = CandidateRepository(db)
        self._score_repo = ScoreRepository(db)

    def get(self, candidate_id: uuid.UUID) -> Candidate | None:
        return self._candidate_repo.get(candidate_id)

    def latest_score(self, candidate_id: uuid.UUID) -> float | None:
        score = self._score_repo.latest_for_candidate(candidate_id)
        return score.overall_score if score else None

    def latest_score_and_job(self, candidate_id: uuid.UUID) -> tuple[float | None, str | None]:
        score = self._score_repo.latest_for_candidate(candidate_id)
        if not score:
            return None, None
        job_title = score.job.title if score.job else None
        return score.overall_score, job_title

    def update_status(self, candidate_id: uuid.UUID, status: str) -> Candidate | None:
        candidate = self._candidate_repo.get(candidate_id)
        if not candidate:
            return None
        updated = self._candidate_repo.update_status(candidate, status)
        self._db.commit()
        self._db.refresh(updated)
        return updated

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
        return self._candidate_repo.search(
            name, email, skill, min_experience, max_experience, status, limit, offset
        )

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Candidate]:
        return self._candidate_repo.list_all(limit, offset)
