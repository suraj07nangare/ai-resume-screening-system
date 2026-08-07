import json
import httpx
from pydantic import BaseModel, ValidationError

from app.core.exceptions import LLMProviderError
from app.services.llm.base import LLMProvider, T

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, base_url: str = "https://api.openai.com/v1") -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")

    def generate_structured(self, system_prompt: str, user_prompt: str, response_model: type[T]) -> T:
        schema = response_model.model_json_schema()
        
        # Embed the schema directly into the system prompt (matching the Anthropic pattern)
        instructions = (
            f"{system_prompt}\n\nRespond ONLY with valid JSON matching this schema, no prose, "
            f"no markdown fences:\n{json.dumps(schema)}"
        )
        
        try:
            response = httpx.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": user_prompt},
                    ],
                    # Switch from json_schema to the universally supported json_object
                    "response_format": {
                        "type": "json_object"
                    },
                },
                timeout=60.0,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            
            # Strip markdown fences in case the provider includes them despite instructions
            content = content.strip().removeprefix("```json").removesuffix("```").strip()
            
            return response_model.model_validate(json.loads(content))
        except (httpx.HTTPError, KeyError, json.JSONDecodeError, ValidationError) as exc:
            raise LLMProviderError(f"OpenAI-compatible extraction failed: {exc}") from exc