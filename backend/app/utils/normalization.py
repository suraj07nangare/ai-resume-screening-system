import re

_SKILL_ALIASES = {
    "postgres": "postgresql",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "gcp": "google cloud platform",
    "aws": "amazon web services",
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node",
    "node.js": "node",
    "sklearn": "scikit-learn",
}


def normalize_skill(name: str) -> str:
    cleaned = name.strip().lower()
    cleaned = re.sub(r"[^a-z0-9\+\#\.\s\-]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return _SKILL_ALIASES.get(cleaned, cleaned)


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()
