import json
from typing import Any

from volcenginesdkarkruntime import Ark

from app.core.config import get_settings


class ArkLLMService:
    """Small wrapper around Volcengine Ark Responses API."""

    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.ark_api_key:
            # Keep this explicit so deployment errors are easy to understand.
            raise RuntimeError("ARK_API_KEY is missing. Set it in environment variables or .env.")
        self.client = Ark(
            base_url=self.settings.ark_base_url,
            api_key=self.settings.ark_api_key,
        )

    def chat(self, system_prompt: str, user_message: str, context: dict[str, Any] | None = None) -> str:
        context_text = json.dumps(context or {}, ensure_ascii=False, indent=2)
        response = self.client.responses.create(
            model=self.settings.ark_model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"上下文：\n{context_text}\n\n用户问题：\n{user_message}",
                        }
                    ],
                },
            ],
        )
        return self._extract_text(response)

    def vision_chat(self, image_url: str, text: str, system_prompt: str | None = None) -> str:
        input_items: list[dict[str, Any]] = []
        if system_prompt:
            input_items.append(
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                }
            )
        input_items.append(
            {
                "role": "user",
                "content": [
                    {"type": "input_image", "image_url": image_url},
                    {"type": "input_text", "text": text},
                ],
            }
        )
        response = self.client.responses.create(
            model=self.settings.ark_model,
            input=input_items,
        )
        return self._extract_text(response)

    def json_chat(self, system_prompt: str, user_message: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Ask the model for JSON and parse it safely.

        If Ark structured output is enabled in your account, replace this with native schema mode.
        """
        raw = self.chat(system_prompt, user_message, context)
        try:
            return json.loads(self._strip_markdown_json(raw))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Model did not return valid JSON: {raw[:500]}") from exc

    @staticmethod
    def _strip_markdown_json(text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```json"):
            stripped = stripped.removeprefix("```json").strip()
        if stripped.startswith("```"):
            stripped = stripped.removeprefix("```").strip()
        if stripped.endswith("```"):
            stripped = stripped.removesuffix("```").strip()
        return stripped

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Best-effort text extraction for Ark Responses API objects."""
        # SDKs may expose output_text directly.
        output_text = getattr(response, "output_text", None)
        if output_text:
            return str(output_text)

        # Fall back to model_dump for pydantic-like response objects.
        if hasattr(response, "model_dump"):
            data = response.model_dump()
        elif isinstance(response, dict):
            data = response
        else:
            return str(response)

        chunks: list[str] = []
        for item in data.get("output", []) or []:
            for content in item.get("content", []) or []:
                if isinstance(content, dict):
                    text = content.get("text") or content.get("output_text")
                    if text:
                        chunks.append(str(text))
        if chunks:
            return "\n".join(chunks)
        return json.dumps(data, ensure_ascii=False)
