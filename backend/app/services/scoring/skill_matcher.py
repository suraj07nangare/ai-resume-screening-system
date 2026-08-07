from dataclasses import dataclass

from app.utils.normalization import normalize_skill

PARTIAL_MATCH_THRESHOLD = 0.6


@dataclass
class SkillMatch:
    skill: str
    match_type: str
    match_score: float
    explanation: str


def _token_overlap(a: str, b: str) -> float:
    tokens_a = set(a.split())
    tokens_b = set(b.split())
    if not tokens_a or not tokens_b:
        return 0.0
    overlap = tokens_a & tokens_b
    return len(overlap) / max(len(tokens_a), len(tokens_b))


def match_skills(candidate_skills: list[str], required_skills: list[str]) -> list[SkillMatch]:
    normalized_candidate = {normalize_skill(s) for s in candidate_skills}
    results: list[SkillMatch] = []

    for required in required_skills:
        norm_required = normalize_skill(required)
        if norm_required in normalized_candidate:
            results.append(
                SkillMatch(required, "matched", 100.0, f"Candidate has direct experience with {required}")
            )
            continue

        best_overlap = 0.0
        for candidate_skill in normalized_candidate:
            overlap = _token_overlap(norm_required, candidate_skill)
            best_overlap = max(best_overlap, overlap)

        if best_overlap >= PARTIAL_MATCH_THRESHOLD:
            results.append(
                SkillMatch(
                    required, "partial", round(best_overlap * 100, 1),
                    f"Candidate has related experience overlapping with {required}",
                )
            )
        else:
            results.append(SkillMatch(required, "missing", 0.0, f"No evidence of {required} in the resume"))

    return results


def calculate_skills_score(matches: list[SkillMatch]) -> float:
    if not matches:
        return 100.0
    total = sum(match.match_score for match in matches)
    return round(total / len(matches), 2)
