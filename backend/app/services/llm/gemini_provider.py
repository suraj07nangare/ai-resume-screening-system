import json

import httpx
from pydantic import ValidationError

from app.core.exceptions import LLMProviderError
from app.services.llm.base import LLMProvider, T


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def generate_structured(self, system_prompt: str, user_prompt: str, response_model: type[T]) -> T:
        schema = response_model.model_json_schema()
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._api_key}"
        )
        try:
            response = httpx.post(
                url,
                json={
                    "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "responseSchema": schema,
                    },
                },
                timeout=60.0,
            )
            response.raise_for_status()
            content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return response_model.model_validate(json.loads(content))
        except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError, ValidationError) as exc:
            raise LLMProviderError(f"Gemini extraction failed: {exc}") from exc
