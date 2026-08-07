from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.core.exceptions import LLMProviderError
from app.schemas.resume import ResumeExtraction
from app.services.llm.base import LLMProvider, T
from app.services.llm.extraction_schemas import JobExtraction
from app.services.llm.mock_provider import MockProvider


def build_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower()

    if provider in ("openai", "groq", "openrouter", "ollama"):
        from app.services.llm.openai_provider import OpenAIProvider

        # 1. Determine API Key
        if provider == "groq":
            api_key = settings.groq_api_key
        elif provider == "openrouter":
            api_key = settings.openrouter_api_key
        else:
            api_key = settings.openai_api_key

        # Allow empty API key for local providers like Ollama
        if not api_key and provider != "ollama":
            raise LLMProviderError(f"API key for {provider} is not configured")

        # 2. Determine Base URL
        if provider == "groq":
            base_url = "https://api.groq.com/openai/v1"
        elif provider == "openrouter":
            base_url = "https://openrouter.ai/api/v1"
        elif provider == "ollama":
            base_url = settings.llm_base_url or "http://localhost:11434/v1"
        else:
            base_url = settings.llm_base_url or "https://api.openai.com/v1"

        return OpenAIProvider(
            api_key=api_key or "sk-no-key", 
            model=settings.llm_model,
            base_url=base_url
        )

    if provider == "anthropic":
        from app.services.llm.anthropic_provider import AnthropicProvider

        if not settings.anthropic_api_key:
            raise LLMProviderError("ANTHROPIC_API_KEY is not configured")
        return AnthropicProvider(api_key=settings.anthropic_api_key, model=settings.llm_model)

    if provider == "gemini":
        from app.services.llm.gemini_provider import GeminiProvider

        if not settings.gemini_api_key:
            raise LLMProviderError("GEMINI_API_KEY is not configured")
        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.llm_model)

    return MockProvider()

RESUME_SYSTEM_PROMPT = (
    "You are an expert technical recruiter and AI resume parser. Extract structured candidate information "
    "from the provided resume text. Adhere strictly to the following rules:\n"
    "1. Total Experience Calculation: To calculate `total_experience_years`, carefully sum the durations of all "
    "professional work experience listed under the employment history. Convert months to fractional years "
    "(e.g., 6 months = 0.5). Do not include education, internships, or personal project durations in this total. "
    "If no professional work experience is found, return 0.0.\n"
    "2. Accuracy: Only extract information explicitly present or strongly implied by the text. Do not invent or "
    "hallucinate names, emails, phone numbers, or degrees.\n"
    "3. Skills Normalization: Extract both explicit skills and those implied by project descriptions (e.g., building "
    "a REST API with FastAPI implies Python). Normalize skill names (e.g., 'React.js' and 'ReactJS' become 'React').\n"
    "4. Missing Data: If a field cannot be accurately determined from the text, return null. Do not guess."
)

JOB_SYSTEM_PROMPT = (
    "You are an expert technical recruiter. Extract structured requirements from the job "
    "description. Separate clearly required skills from preferred/nice-to-have skills."
)


class LLMService:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider or build_provider(get_settings())

    def extract_resume(self, resume_text: str, max_retries: int = 2) -> ResumeExtraction:
        return self._extract_with_retry(RESUME_SYSTEM_PROMPT, resume_text, ResumeExtraction, max_retries)

    def extract_job(self, job_description: str, max_retries: int = 2) -> JobExtraction:
        return self._extract_with_retry(JOB_SYSTEM_PROMPT, job_description, JobExtraction, max_retries)

    def _extract_with_retry(
        self, system_prompt: str, user_prompt: str, response_model: type[T], max_retries: int
    ) -> T:
        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                return self._provider.generate_structured(system_prompt, user_prompt, response_model)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        raise LLMProviderError(f"LLM extraction failed after {max_retries + 1} attempts: {last_error}")