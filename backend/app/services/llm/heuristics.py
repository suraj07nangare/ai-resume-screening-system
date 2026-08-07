import re

COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "postgresql", "mysql", "mongodb", "redis",
    "fastapi", "django", "flask", "react", "angular", "vue", "node",
    "docker", "kubernetes", "aws", "gcp", "azure", "terraform",
    "machine learning", "deep learning", "nlp", "computer vision",
    "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy",
    "git", "linux", "ci/cd", "rest api", "graphql", "microservices",
    "spring boot", "html", "css", "streamlit", "langchain", "langgraph",
]


def extract_email(text: str) -> str | None:
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\d{10}", text)
    return match.group(0) if match else None


def extract_name(text: str) -> str | None:
    for line in text.split("\n")[:5]:
        candidate = line.strip()
        if 2 <= len(candidate.split()) <= 4 and candidate.replace(" ", "").isalpha():
            return candidate
    return None


def extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for skill in COMMON_SKILLS:
        if skill in lowered:
            found.append(skill)
    return found


def extract_experience_years(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", text.lower())
    if match:
        return float(match.group(1))
    return None
