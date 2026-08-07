from pydantic import BaseModel

from app.schemas.resume import ResumeExtraction
from app.services.llm import heuristics
from app.services.llm.base import LLMProvider, T
from app.services.llm.extraction_schemas import JobExtraction


class MockProvider(LLMProvider):
    def generate_structured(self, system_prompt: str, user_prompt: str, response_model: type[T]) -> T:
        if response_model is ResumeExtraction:
            return self._extract_resume(user_prompt)  # type: ignore[return-value]
        if response_model is JobExtraction:
            return self._extract_job(user_prompt)  # type: ignore[return-value]
        return response_model()

    def _extract_resume(self, text: str) -> ResumeExtraction:
        return ResumeExtraction(
            name=heuristics.extract_name(text),
            email=heuristics.extract_email(text),
            phone=heuristics.extract_phone(text),
            skills=heuristics.extract_skills(text),
            total_experience_years=heuristics.extract_experience_years(text),
            summary=text[:280].strip() if text else None,
        )

    def _extract_job(self, text: str) -> JobExtraction:
        skills = heuristics.extract_skills(text)
        split = max(1, len(skills) - max(1, len(skills) // 3))
        return JobExtraction(
            required_skills=skills[:split],
            preferred_skills=skills[split:],
            minimum_experience_years=heuristics.extract_experience_years(text),
        )
