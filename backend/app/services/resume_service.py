import shutil
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ExtractionError
from app.db.models.candidate import Candidate
from app.db.models.resume_file import ResumeFile
from app.db.repositories.candidate_repository import CandidateRepository
from app.db.repositories.resume_repository import ResumeRepository
from app.db.repositories.skill_repository import SkillRepository
from app.schemas.resume import ResumeExtraction
from app.services.llm.llm_service import LLMService
from app.services.parsing.resume_extractor import extract_resume_text
from app.utils.file_validation import validate_upload

UPLOAD_DIR = Path("storage/resumes")


class ResumeService:
    def __init__(self, db: Session, llm_service: LLMService | None = None) -> None:
        self._db = db
        self._resume_repo = ResumeRepository(db)
        self._candidate_repo = CandidateRepository(db)
        self._skill_repo = SkillRepository(db)
        self._llm_service = llm_service or LLMService()

    def process_upload(self, filename: str, content: bytes) -> ResumeFile:
        extension = validate_upload(filename, len(content))

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid.uuid4()}.{extension}"
        stored_path = UPLOAD_DIR / stored_name
        stored_path.write_bytes(content)

        resume_file = ResumeFile(
            filename=filename,
            file_type=extension,
            file_size=len(content),
            storage_path=str(stored_path),
            extraction_status="processing",
        )
        self._resume_repo.create(resume_file)

        try:
            text, method = extract_resume_text(str(stored_path), extension)
            resume_file.raw_text = text
            resume_file.extraction_method = method

            extraction = self._llm_service.extract_resume(text)
            candidate = self._persist_candidate(extraction)

            resume_file.candidate_id = candidate.id
            resume_file.extraction_status = "completed"
        except ExtractionError as exc:
            resume_file.extraction_status = "failed"
            resume_file.error_message = str(exc)
        except Exception as exc:  # noqa: BLE001
            resume_file.extraction_status = "failed"
            resume_file.error_message = "Resume extraction failed due to an internal error"

        self._resume_repo.update(resume_file)
        self._db.commit()
        self._db.refresh(resume_file)
        return resume_file

    def _persist_candidate(self, extraction: ResumeExtraction) -> Candidate:
        candidate = Candidate(
            name=extraction.name or "Unknown Candidate",
            email=extraction.email,
            phone=extraction.phone,
            total_experience_years=extraction.total_experience_years,
            education_summary=extraction.education_summary
            or ("; ".join(f"{e.degree} - {e.institution}" for e in extraction.education if e.degree) or None),
            summary=extraction.summary,
        )
        self._candidate_repo.create(candidate)

        for skill_name in extraction.skills:
            skill = self._skill_repo.get_or_create(skill_name)
            self._candidate_repo.add_skill(candidate.id, skill.id, source="resume")

        self._db.flush()
        return candidate

    def get(self, resume_id: uuid.UUID) -> ResumeFile | None:
        return self._resume_repo.get(resume_id)
