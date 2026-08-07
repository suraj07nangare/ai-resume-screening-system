import uuid

from sqlalchemy.orm import Session

from app.db.models.job import Job
from app.db.repositories.job_repository import JobRepository
from app.schemas.job import JobCreate
from app.services.llm.llm_service import LLMService


class JobService:
    def __init__(self, db: Session, llm_service: LLMService | None = None) -> None:
        self._db = db
        self._job_repo = JobRepository(db)
        self._llm_service = llm_service or LLMService()

    def create_job(self, payload: JobCreate) -> Job:
        extraction = self._llm_service.extract_job(payload.raw_description)

        job = Job(
            title=payload.title,
            raw_description=payload.raw_description,
            required_skills="|".join(extraction.required_skills) or None,
            preferred_skills="|".join(extraction.preferred_skills) or None,
            responsibilities="|".join(extraction.responsibilities) or None,
            qualifications="|".join(extraction.qualifications) or None,
            minimum_experience_years=extraction.minimum_experience_years,
            education_requirement=extraction.education_requirements,
        )
        self._job_repo.create(job)
        self._db.commit()
        self._db.refresh(job)
        return job

    def get(self, job_id: uuid.UUID) -> Job | None:
        return self._job_repo.get(job_id)

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Job]:
        return self._job_repo.list_all(limit, offset)
