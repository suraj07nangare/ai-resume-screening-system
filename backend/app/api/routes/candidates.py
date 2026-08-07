import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.core.exceptions import NotFoundError
from app.schemas.candidate import (
    CandidateDetail,
    CandidateListItem,
    CandidateListResponse,
    CandidateStatusUpdate,
)
from app.schemas.skill import SkillRead
from app.services.candidate_service import CandidateService

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


def _to_list_item(candidate, latest_score: float | None, latest_job_title: str | None) -> CandidateListItem:
    return CandidateListItem(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        total_experience_years=candidate.total_experience_years,
        education_summary=candidate.education_summary,
        summary=candidate.summary,
        status=candidate.status,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at,
        skills=[cs.skill.name for cs in candidate.candidate_skills],
        resume_status="processed" if candidate.candidate_skills else "no_skills_extracted",
        latest_score=latest_score,
        latest_job_title=latest_job_title,
    )


@router.get("", response_model=CandidateListResponse)
def list_candidates(
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_session),
) -> CandidateListResponse:
    service = CandidateService(db)
    candidates = service.list_all(limit, offset)
    items = []
    for c in candidates:
        score, job_title = service.latest_score_and_job(c.id)
        items.append(_to_list_item(c, score, job_title))
    return CandidateListResponse(items=items, total=len(items), limit=limit, offset=offset)


@router.get("/search", response_model=CandidateListResponse)
def search_candidates(
    name: str | None = None,
    email: str | None = None,
    skill: str | None = None,
    min_experience: float | None = None,
    max_experience: float | None = None,
    status: str | None = None,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_session),
) -> CandidateListResponse:
    service = CandidateService(db)
    candidates, total = service.search(
        name, email, skill, min_experience, max_experience, status, limit, offset
    )
    items = []
    for c in candidates:
        score, job_title = service.latest_score_and_job(c.id)
        items.append(_to_list_item(c, score, job_title))
    return CandidateListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{candidate_id}", response_model=CandidateDetail)
def get_candidate(candidate_id: uuid.UUID, db: Session = Depends(get_session)) -> CandidateDetail:
    service = CandidateService(db)
    candidate = service.get(candidate_id)
    if not candidate:
        raise NotFoundError(f"Candidate {candidate_id} was not found")

    skills = [SkillRead.model_validate(cs.skill) for cs in candidate.candidate_skills]
    score, job_title = service.latest_score_and_job(candidate.id)
    return CandidateDetail(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        total_experience_years=candidate.total_experience_years,
        education_summary=candidate.education_summary,
        summary=candidate.summary,
        status=candidate.status,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at,
        skills=skills,
        latest_score=score,
        latest_job_title=job_title,
    )


@router.patch("/{candidate_id}/status", response_model=CandidateDetail)
def update_candidate_status(
    candidate_id: uuid.UUID, payload: CandidateStatusUpdate, db: Session = Depends(get_session)
) -> CandidateDetail:
    service = CandidateService(db)
    candidate = service.update_status(candidate_id, payload.status)
    if not candidate:
        raise NotFoundError(f"Candidate {candidate_id} was not found")

    skills = [SkillRead.model_validate(cs.skill) for cs in candidate.candidate_skills]
    score, job_title = service.latest_score_and_job(candidate.id)
    return CandidateDetail(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        total_experience_years=candidate.total_experience_years,
        education_summary=candidate.education_summary,
        summary=candidate.summary,
        status=candidate.status,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at,
        skills=skills,
        latest_score=score,
        latest_job_title=job_title,
    )
