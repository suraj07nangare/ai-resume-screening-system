import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.models.score import Score
from app.db.models.score_skill import ScoreSkill
from app.db.repositories.candidate_repository import CandidateRepository
from app.db.repositories.job_repository import JobRepository
from app.db.repositories.score_repository import ScoreRepository
from app.db.repositories.skill_repository import SkillRepository
from app.services.scoring.scorer import screen_candidate


class ScreeningService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._candidate_repo = CandidateRepository(db)
        self._job_repo = JobRepository(db)
        self._score_repo = ScoreRepository(db)
        self._skill_repo = SkillRepository(db)

    def screen(self, candidate_id: uuid.UUID, job_id: uuid.UUID) -> Score:
        candidate = self._candidate_repo.get(candidate_id)
        if not candidate:
            raise NotFoundError(f"Candidate {candidate_id} was not found")

        job = self._job_repo.get(job_id)
        if not job:
            raise NotFoundError(f"Job {job_id} was not found")

        candidate_skills = [cs.skill.name for cs in candidate.candidate_skills]
        required_skills = (job.required_skills or "").split("|") if job.required_skills else []
        required_skills = [s for s in required_skills if s]

        outcome = screen_candidate(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            candidate_experience_years=candidate.total_experience_years,
            required_experience_years=job.minimum_experience_years,
            candidate_education=candidate.education_summary,
            required_education=job.education_requirement,
        )

        matched = [m.skill for m in outcome.skill_matches if m.match_type == "matched"]
        partial = [m.skill for m in outcome.skill_matches if m.match_type == "partial"]
        missing = [m.skill for m in outcome.skill_matches if m.match_type == "missing"]

        summary = (
            f"Overall match of {outcome.overall_score}/100 for {job.title}. "
            f"{len(matched)} matched, {len(partial)} partial, {len(missing)} missing skills."
        )

        explanation_lines = [
            f"Overall Score: {outcome.overall_score}",
            "",
            "Matched Skills:",
            *([f"- {s}" for s in matched] if matched else ["- None"]),
            "",
            "Partial Matches:",
            *([f"- {s}" for s in partial] if partial else ["- None"]),
            "",
            "Missing Skills:",
            *([f"- {s}" for s in missing] if missing else ["- None"]),
            "",
            f"Experience: {outcome.experience_explanation}",
            f"Education: {outcome.education_explanation}",
            "",
            "Strengths:",
            *[f"- {s}" for s in outcome.strengths],
            "",
            "Gaps:",
            *[f"- {g}" for g in outcome.gaps],
        ]
        explanation = "\n".join(explanation_lines)

        score = Score(
            candidate_id=candidate.id,
            job_id=job.id,
            overall_score=outcome.overall_score,
            skills_score=outcome.skills_score,
            experience_score=outcome.experience_score,
            education_score=outcome.education_score,
            other_score=outcome.other_score,
            ai_summary=summary,
            explanation=explanation,
        )
        self._score_repo.create(score)

        for match in outcome.skill_matches:
            skill = self._skill_repo.get_or_create(match.skill)
            self._score_repo.add_score_skill(
                ScoreSkill(
                    score_id=score.id,
                    skill_id=skill.id,
                    match_type=match.match_type,
                    match_score=match.match_score,
                    explanation=match.explanation,
                )
            )

        self._db.commit()
        self._db.refresh(score)
        return score

    def get(self, score_id: uuid.UUID) -> Score | None:
        return self._score_repo.get(score_id)

    def rankings_for_job(self, job_id: uuid.UUID) -> list[Score]:
        job = self._job_repo.get(job_id)
        if not job:
            raise NotFoundError(f"Job {job_id} was not found")
        return self._score_repo.rankings_for_job(job_id)
