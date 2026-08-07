import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.resume_file import ResumeFile


class ResumeRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, resume_file: ResumeFile) -> ResumeFile:
        self._db.add(resume_file)
        self._db.flush()
        return resume_file

    def get(self, resume_id: uuid.UUID) -> ResumeFile | None:
        return self._db.execute(select(ResumeFile).where(ResumeFile.id == resume_id)).scalar_one_or_none()

    def update(self, resume_file: ResumeFile) -> ResumeFile:
        self._db.add(resume_file)
        self._db.flush()
        return resume_file
