_LEVELS = {
    "phd": 5,
    "doctorate": 5,
    "master": 4,
    "m.tech": 4,
    "mca": 4,
    "mba": 4,
    "bachelor": 3,
    "b.tech": 3,
    "b.e": 3,
    "be": 3,
    "bsc": 3,
    "diploma": 2,
    "high school": 1,
}


def _detect_level(text: str | None) -> int:
    if not text:
        return 0
    lowered = text.lower()
    best = 0
    for key, level in _LEVELS.items():
        if key in lowered:
            best = max(best, level)
    return best


def calculate_education_score(candidate_education: str | None, required_education: str | None) -> tuple[float, str]:
    if not required_education:
        return 100.0, "No specific education requirement was specified for this role."

    candidate_level = _detect_level(candidate_education)
    required_level = _detect_level(required_education)

    if required_level == 0:
        return 100.0, "Education requirement could not be interpreted; not penalizing the candidate."

    if candidate_level == 0:
        return 50.0, "Candidate's education level could not be clearly determined from the resume."

    if candidate_level >= required_level:
        return 100.0, f"Candidate's education meets or exceeds the requirement ({required_education})."

    gap = required_level - candidate_level
    score = max(0.0, 100 - gap * 30)
    return score, f"Candidate's education level is below the stated requirement ({required_education})."
