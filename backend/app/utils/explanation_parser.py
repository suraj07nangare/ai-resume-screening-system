def parse_strengths_and_gaps(explanation: str) -> tuple[list[str], list[str]]:
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