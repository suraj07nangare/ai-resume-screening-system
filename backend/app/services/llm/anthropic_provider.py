import json

import httpx
from pydantic import ValidationError

from app.core.exceptions import LLMProviderError
from app.services.llm.base import LLMProvider, T


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def generate_structured(self, system_prompt: str, user_prompt: str, response_model: type[T]) -> T:
        schema = response_model.model_json_schema()
        instructions = (
            f"{system_prompt}\n\nRespond ONLY with valid JSON matching this schema, no prose, "
            f"no markdown fences:\n{json.dumps(schema)}"
        )
        try:
            response = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self._api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self._model,
                    "max_tokens": 2000,
                    "system": instructions,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
                timeout=60.0,
            )
            response.raise_for_status()
            content = response.json()["content"][0]["text"]
            content = content.strip().removeprefix("```json").removesuffix("```").strip()
            return response_model.model_validate(json.loads(content))
        except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError, ValidationError) as exc:
            raise LLMProviderError(f"Anthropic extraction failed: {exc}") from exc
