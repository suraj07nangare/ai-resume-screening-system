import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.job import Job


class JobRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, job: Job) -> Job:
        self._db.add(job)
        self._db.flush()
        return job

    def get(self, job_id: uuid.UUID) -> Job | None:
        return self._db.execute(select(Job).where(Job.id == job_id)).scalar_one_or_none()

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Job]:
        stmt = select(Job).order_by(Job.created_at.desc()).limit(limit).offset(offset)
        return list(self._db.execute(stmt).scalars())
