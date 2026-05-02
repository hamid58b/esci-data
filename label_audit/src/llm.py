import json
from pathlib import Path

from openai import OpenAI


class LLMClient:
    def __init__(self, model: str, prompt_path: Path):
        self._model = model
        self._prompt_template = prompt_path.read_text()
        self._client = OpenAI()

    def audit_pair(
        self,
        query: str,
        product_title: str,
        product_description: str,
        product_bullet_point: str,
    ) -> dict:
        prompt = self._prompt_template.format(
            query=query,
            product_title=product_title or "",
            product_description=product_description or "",
            product_bullet_point=product_bullet_point or "",
        )
        for attempt in range(2):
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
            try:
                result = json.loads(raw)
                return {
                    "accurate": bool(result["accurate"]),
                    "reformulated_query": result.get("reformulated_query"),
                }
            except (json.JSONDecodeError, KeyError):
                if attempt == 1:
                    raise ValueError(f"Unparseable LLM response after 2 attempts: {raw}")
