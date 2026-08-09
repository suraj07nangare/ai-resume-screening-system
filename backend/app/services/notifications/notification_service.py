import logging
import uuid

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.db.repositories.candidate_repository import CandidateRepository
from app.services.notifications.email_service import EmailService
from app.services.notifications.scheduling import build_scheduling_link
from app.services.notifications.templates import rejection_email, shortlist_email, under_review_email

logger = logging.getLogger(__name__)


def notify_candidate_of_screening(
    candidate_id: uuid.UUID,
    candidate_name: str,
    candidate_email: str | None,
    job_title: str,
    overall_score: float,
    strengths: list[str],
    gaps: list[str],
) -> None:
    settings = get_settings()

    if not settings.notifications_enabled:
        return

    if not candidate_email:
        logger.info("Skipping notification for candidate %s: no email on file", candidate_id)
        return

    scheduling_link: str | None = None

    if overall_score >= settings.shortlist_score_threshold:
        new_status = "shortlisted"
        if overall_score >= settings.schedule_link_score_threshold:
            scheduling_link = build_scheduling_link(settings, candidate_name, candidate_email)
        subject, body = shortlist_email(
            candidate_name, job_title, settings.company_name, overall_score, strengths, scheduling_link
        )
    elif overall_score < settings.reject_score_threshold:
        new_status = "rejected"
        subject, body = rejection_email(candidate_name, job_title, settings.company_name, gaps)
    else:
        new_status = None
        subject, body = under_review_email(candidate_name, job_title, settings.company_name, overall_score)

    email_service = EmailService()
    sent = email_service.send(candidate_email, subject, body)
    logger.info(
        "Notification for candidate %s (status=%s, scheduling_link=%s): sent=%s",
        candidate_id, new_status or "under_review", bool(scheduling_link), sent,
    )

    if new_status and settings.auto_update_candidate_status:
        db: Session = SessionLocal()
        try:
            repo = CandidateRepository(db)
            candidate = repo.get(candidate_id)
            if candidate:
                repo.update_status(candidate, new_status)
                db.commit()
        finally:
            db.close()