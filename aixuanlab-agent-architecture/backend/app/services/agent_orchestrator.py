from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    FormulaErrorRequest,
    FormulaErrorResponse,
    GeneratePracticeRequest,
    PracticeQuestion,
)
from app.services.ai_context_service import AIContextService
from app.services.ark_llm_service import ArkLLMService
from app.services.practice_service import PracticeService


EXCEL_COACH_SYSTEM_PROMPT = """
你是 aixuanlab.com 的 Excel 学习教练。你的任务不是闲聊，而是帮助用户学习中文职场 Excel。
回答要求：
1. 用中文，表达清楚，适合初学者。
2. 优先结合用户画像、最近做题记录、函数掌握度、当前题目和学习记忆。
3. 解释公式错误时，要指出错因、给提示，必要时再给正确公式。
4. 生成练习题时，必须贴近真实职场场景：行政、人事、财务、运营、销售。
5. 不要编造用户数据；上下文没有的信息要说明不确定。
"""


class AgentOrchestrator:
    """Main workflow Agent. Keep it deterministic in MVP."""

    def __init__(self) -> None:
        self.llm = ArkLLMService()
        self.context_service = AIContextService()
        self.practice_service = PracticeService(self.llm)

    def chat(self, user_id: str, request: ChatRequest) -> ChatResponse:
        context = self.context_service.build_context(
            user_id=user_id,
            current_practice_id=request.current_practice_id,
            conversation_id=request.conversation_id,
        )
        answer = self.llm.chat(
            system_prompt=EXCEL_COACH_SYSTEM_PROMPT,
            user_message=request.message,
            context=context,
        )
        return ChatResponse(
            answer=answer,
            conversation_id=request.conversation_id,
            used_context={"has_user_profile": True, "has_learning_context": True},
        )

    def generate_practice(self, user_id: str, request: GeneratePracticeRequest) -> PracticeQuestion:
        context = self.context_service.build_context(user_id=user_id)
        return self.practice_service.generate_practice(request, context)

    def explain_formula_error(self, user_id: str, request: FormulaErrorRequest) -> FormulaErrorResponse:
        context = self.context_service.build_context(user_id=user_id, current_practice_id=request.practice_id)
        payload = {
            "practice_id": request.practice_id,
            "target_cell": request.target_cell,
            "user_formula": request.user_formula,
            "expected_formula": request.expected_formula,
            "sheet_context": request.sheet_context,
            "learning_context": context,
        }
        system_prompt = EXCEL_COACH_SYSTEM_PROMPT + """

请你作为公式批改老师，返回严格 JSON，字段为：
{
  "is_correct": boolean,
  "error_type": "wrong_function|wrong_range|wrong_condition|syntax_error|absolute_ref_error|missing_condition|logic_reversed|unknown",
  "explanation": "中文解释",
  "hint": "提示",
  "correct_formula": "正确公式或 null"
}
"""
        result = self.llm.json_chat(
            system_prompt=system_prompt,
            user_message="请判断用户公式是否正确，并解释原因。",
            context=payload,
        )
        return FormulaErrorResponse(**result)
