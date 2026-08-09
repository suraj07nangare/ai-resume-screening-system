import uuid

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.core.exceptions import NotFoundError
from app.schemas.screening import ScreeningCreate, ScreeningResult
from app.services.notifications.notification_service import notify_candidate_of_screening
from app.services.screening.screening_service import ScreeningService
from app.utils.explanation_parser import parse_strengths_and_gaps

router = APIRouter(prefix="/api/screenings", tags=["screenings"])


def _to_result(score) -> ScreeningResult:
    matched = [ss.skill.name for ss in score.score_skills if ss.match_type == "matched"]
    partial = [ss.skill.name for ss in score.score_skills if ss.match_type == "partial"]
    missing = [ss.skill.name for ss in score.score_skills if ss.match_type == "missing"]

    strengths, gaps = parse_strengths_and_gaps(score.explanation or "")
    return ScreeningResult(
        id=score.id,
        candidate_id=score.candidate_id,
        job_id=score.job_id,
        overall_score=score.overall_score,
        skills_score=score.skills_score,
        experience_score=score.experience_score,
        education_score=score.education_score,
        other_score=score.other_score,
        matched_skills=matched,
        partial_skills=partial,
        missing_skills=missing,
        strengths=strengths,
        gaps=gaps,
        ai_summary=score.ai_summary,
        explanation=score.explanation or "",
        created_at=score.created_at,
    )


@router.post("", response_model=ScreeningResult, status_code=201)
def create_screening(
    payload: ScreeningCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
) -> ScreeningResult:
    service = ScreeningService(db)
    score = service.screen(payload.candidate_id, payload.job_id)
    result = _to_result(score)

    background_tasks.add_task(
        notify_candidate_of_screening,
        candidate_id=score.candidate_id,
        candidate_name=score.candidate.name,
        candidate_email=score.candidate.email,
        job_title=score.job.title,
        overall_score=score.overall_score,
        strengths=result.strengths,
        gaps=result.gaps,
    )

    return result


@router.get("/{screening_id}", response_model=ScreeningResult)
def get_screening(screening_id: uuid.UUID, db: Session = Depends(get_session)) -> ScreeningResult:
    service = ScreeningService(db)
    score = service.get(screening_id)
    if not score:
        raise NotFoundError(f"Screening {screening_id} was not found")
    return _to_result(score)