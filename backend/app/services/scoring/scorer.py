from dataclasses import dataclass, field

from app.core.config import get_settings
from app.services.scoring.education_matcher import calculate_education_score
from app.services.scoring.experience_matcher import calculate_experience_score
from app.services.scoring.skill_matcher import SkillMatch, calculate_skills_score, match_skills


@dataclass
class ScreeningOutcome:
    overall_score: float
    skills_score: float
    experience_score: float
    education_score: float
    other_score: float
    skill_matches: list[SkillMatch] = field(default_factory=list)
    experience_explanation: str = ""
    education_explanation: str = ""
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)


def screen_candidate(
    candidate_skills: list[str],
    required_skills: list[str],
    candidate_experience_years: float | None,
    required_experience_years: float | None,
    candidate_education: str | None,
    required_education: str | None,
) -> ScreeningOutcome:
    settings = get_settings()

    skill_matches = match_skills(candidate_skills, required_skills)
    skills_score = calculate_skills_score(skill_matches)

    experience_score, experience_explanation = calculate_experience_score(
        candidate_experience_years, required_experience_years
    )
    education_score, education_explanation = calculate_education_score(candidate_education, required_education)

    other_score = 100.0

    overall_score = round(
        skills_score * settings.skills_weight
        + experience_score * settings.experience_weight
        + education_score * settings.education_weight
        + other_score * settings.other_weight,
        2,
    )

    strengths: list[str] = []
    gaps: list[str] = []

    matched = [m.skill for m in skill_matches if m.match_type == "matched"]
    missing = [m.skill for m in skill_matches if m.match_type == "missing"]

    if matched:
        strengths.append(f"Strong alignment on: {', '.join(matched[:5])}")
    if experience_score >= 100:
        strengths.append("Meets or exceeds the required experience level")
    if education_score >= 100:
        strengths.append("Education background matches the role requirement")

    if missing:
        gaps.append(f"No clear evidence of: {', '.join(missing[:5])}")
    if experience_score < 100:
        gaps.append(experience_explanation)
    if education_score < 100:
        gaps.append(education_explanation)

    if not strengths:
        strengths.append("Candidate profile reviewed against role requirements")
    if not gaps:
        gaps.append("No significant gaps identified against the stated requirements")

    return ScreeningOutcome(
        overall_score=overall_score,
        skills_score=skills_score,
        experience_score=experience_score,
        education_score=education_score,
        other_score=other_score,
        skill_matches=skill_matches,
        experience_explanation=experience_explanation,
        education_explanation=education_explanation,
        strengths=strengths,
        gaps=gaps,
    )
