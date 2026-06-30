from app.schemas.ai import GeneratePracticeRequest, PracticeQuestion
from app.services.ark_llm_service import ArkLLMService


class PracticeService:
    """Generate and search Excel practice questions."""

    def __init__(self, llm: ArkLLMService) -> None:
        self.llm = llm

    def generate_practice(self, request: GeneratePracticeRequest, context: dict) -> PracticeQuestion:
        system_prompt = """
你是 aixuanlab.com 的 Excel 练习题生成器。
请根据用户的岗位、函数、难度、场景，生成一道中文职场 Excel 练习题。
必须返回严格 JSON，不要 Markdown，不要解释。

JSON 字段：
{
  "title": string,
  "role": string | null,
  "difficulty": "easy" | "medium" | "hard",
  "function_tags": string[],
  "scenario": string | null,
  "headers": string[],
  "rows": any[][],
  "target_cell": string,
  "answer_formula": string,
  "hints": string[],
  "common_errors": [{"error_type": string, "explanation": string}]
}

要求：
1. 数据要像真实办公表，不要像数学题。
2. 行数控制在 5-10 行，适合网页练习。
3. answer_formula 必须是 Excel 公式。
4. common_errors 要写初学者常见错误。
"""
        payload = {
            "request": request.model_dump(),
            "user_context": context,
        }
        result = self.llm.json_chat(
            system_prompt=system_prompt,
            user_message="请生成一道适合 aixuanlab.com 的 Excel 在线练习题。",
            context=payload,
        )
        return PracticeQuestion(**result)

    def search_practice_library(self, keyword: str | None = None, function_tags: list[str] | None = None) -> list[dict]:
        """Replace with real search over the existing 50 exercises."""
        return []
