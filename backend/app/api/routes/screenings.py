import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.core.exceptions import NotFoundError
from app.schemas.screening import ScreeningCreate, ScreeningResult
from app.services.screening.screening_service import ScreeningService

router = APIRouter(prefix="/api/screenings", tags=["screenings"])


def _to_result(score) -> ScreeningResult:
    matched = [ss.skill.name for ss in score.score_skills if ss.match_type == "matched"]
    partial = [ss.skill.name for ss in score.score_skills if ss.match_type == "partial"]
    missing = [ss.skill.name for ss in score.score_skills if ss.match_type == "missing"]

    strengths, gaps = _parse_strengths_and_gaps(score.explanation or "")
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
        gaps=strengths,
        ai_summary=score.ai_summary,
        explanation=score.explanation or "",
        created_at=score.created_at,
    )


def _parse_strengths_and_gaps(explanation: str) -> tuple[list[str], list[str]]:
    strengths: list[str] = []
    gaps: list[str] = []
    section = None
    for line in explanation.split("\n"):
        stripped = line.strip()
        if stripped == "Strengths:":
            section = "strengths"
            continue
        if stripped == "Gaps:":
            section = "gaps"
            continue
        if stripped.startswith("- ") and section == "strengths":
            strengths.append(stripped[2:])
        elif stripped.startswith("- ") and section == "gaps":
            gaps.append(stripped[2:])
        elif stripped == "":
            continue
        elif section in ("strengths", "gaps") and not stripped.startswith("-"):
            section = None
    return strengths, gaps


@router.post("", response_model=ScreeningResult, status_code=201)
def create_screening(payload: ScreeningCreate, db: Session = Depends(get_session)) -> ScreeningResult:
    service = ScreeningService(db)
    score = service.screen(payload.candidate_id, payload.job_id)
    return _to_result(score)


@router.get("/{screening_id}", response_model=ScreeningResult)
def get_screening(screening_id: uuid.UUID, db: Session = Depends(get_session)) -> ScreeningResult:
    service = ScreeningService(db)
    score = service.get(screening_id)
    if not score:
        raise NotFoundError(f"Screening {screening_id} was not found")
    return _to_result(score)
