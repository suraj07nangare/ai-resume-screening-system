def calculate_experience_score(candidate_years: float | None, required_years: float | None) -> tuple[float, str]:
    if required_years is None or required_years <= 0:
        return 100.0, "No minimum experience requirement was specified for this role."

    if candidate_years is None:
        return 0.0, "Candidate's total experience could not be determined from the resume."

    if candidate_years >= required_years:
        return 100.0, f"Candidate has {candidate_years} years, meeting the {required_years}-year requirement."

    ratio = candidate_years / required_years
    score = round(max(0.0, ratio) * 100, 2)
    explanation = (
        f"Candidate has {candidate_years} years against a requirement of {required_years} years."
    )
    return score, explanation
