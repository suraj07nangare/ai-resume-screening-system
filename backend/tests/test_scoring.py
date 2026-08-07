from app.services.scoring.scorer import screen_candidate


def test_full_skill_match_gives_high_score():
    outcome = screen_candidate(
        candidate_skills=["Python", "FastAPI", "SQL"],
        required_skills=["python", "fastapi", "sql"],
        candidate_experience_years=3,
        required_experience_years=2,
        candidate_education="Bachelor of Engineering",
        required_education="Bachelor",
    )
    assert outcome.overall_score >= 90


def test_missing_skills_lower_score():
    outcome = screen_candidate(
        candidate_skills=["Java"],
        required_skills=["python", "fastapi", "aws"],
        candidate_experience_years=1,
        required_experience_years=5,
        candidate_education=None,
        required_education="Master",
    )
    assert outcome.overall_score < 50


def test_score_always_in_range():
    outcome = screen_candidate([], [], None, None, None, None)
    assert 0 <= outcome.overall_score <= 100
