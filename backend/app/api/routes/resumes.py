import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.core.exceptions import NotFoundError
from app.schemas.candidate import CandidateRead
from app.schemas.resume import ResumeFileRead, ResumeUploadResponse
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...), db: Session = Depends(get_session)
) -> ResumeUploadResponse:
    content = await file.read()
    service = ResumeService(db)
    resume_file = service.process_upload(file.filename or "resume", content)

    candidate_read = None
    if resume_file.candidate:
        candidate_read = CandidateRead.model_validate(resume_file.candidate)

    return ResumeUploadResponse(
        resume_file=ResumeFileRead.model_validate(resume_file),
        candidate=candidate_read,
    )


@router.get("/{resume_id}", response_model=ResumeFileRead)
def get_resume(resume_id: uuid.UUID, db: Session = Depends(get_session)) -> ResumeFileRead:
    service = ResumeService(db)
    resume_file = service.get(resume_id)
    if not resume_file:
        raise NotFoundError(f"Resume {resume_id} was not found")
    return ResumeFileRead.model_validate(resume_file)
