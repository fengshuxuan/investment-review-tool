import json
from app.schemas.ai import TableRecognitionResponse
from app.services.ark_llm_service import ArkLLMService


class ImageTableService:
    """Use Ark multimodal model to recognize table screenshots."""

    def __init__(self) -> None:
        self.llm = ArkLLMService()

    def recognize_table_from_url(self, image_url: str) -> TableRecognitionResponse:
        system_prompt = """
你是 Excel 表格截图识别助手。
请识别图片中的表格结构，并返回严格 JSON，不要 Markdown。
JSON 字段：
{
  "headers": string[],
  "rows": any[][],
  "confidence": number,
  "notes": string | null
}
要求：
1. 如果看不清，confidence 降低，并在 notes 说明。
2. 不要编造看不见的数据。
3. 保留中文表头。
"""
        raw = self.llm.vision_chat(
            image_url=image_url,
            text="请识别这张图片里的表格，返回 JSON。",
            system_prompt=system_prompt,
        )
        try:
            data = json.loads(self.llm._strip_markdown_json(raw))
        except json.JSONDecodeError:
            data = {
                "headers": [],
                "rows": [],
                "confidence": 0.0,
                "notes": f"模型没有返回合法 JSON，需要人工确认。原始返回：{raw[:300]}",
            }
        return TableRecognitionResponse(**data)
