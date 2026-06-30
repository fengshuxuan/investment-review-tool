from typing import Any, Literal
from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    """Resolved authenticated user. In production, do not accept user_id from request body."""

    user_id: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: str | None = None
    current_practice_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str | None = None
    used_context: dict[str, Any] = Field(default_factory=dict)


class GeneratePracticeRequest(BaseModel):
    role: str | None = Field(default=None, description="岗位：行政/人事/财务/运营/销售")
    function_tags: list[str] = Field(default_factory=list)
    difficulty: Literal["easy", "medium", "hard"] = "easy"
    scenario: str | None = None


class PracticeQuestion(BaseModel):
    title: str
    role: str | None = None
    difficulty: str
    function_tags: list[str]
    scenario: str | None = None
    headers: list[str]
    rows: list[list[Any]]
    target_cell: str
    answer_formula: str
    hints: list[str] = Field(default_factory=list)
    common_errors: list[dict[str, Any]] = Field(default_factory=list)


class FormulaErrorRequest(BaseModel):
    practice_id: str
    target_cell: str
    user_formula: str
    expected_formula: str | None = None
    sheet_context: dict[str, Any] = Field(default_factory=dict)


class FormulaErrorResponse(BaseModel):
    is_correct: bool
    error_type: str
    explanation: str
    hint: str | None = None
    correct_formula: str | None = None


class TableRecognitionResponse(BaseModel):
    headers: list[str]
    rows: list[list[Any]]
    confidence: float = 0.0
    notes: str | None = None


class ExcelGenerateRequest(BaseModel):
    practice: PracticeQuestion
    include_answer_sheet: bool = True


class ExcelGenerateResponse(BaseModel):
    file_id: str
    download_url: str


class AgentIntent(BaseModel):
    intent: Literal[
        "chat",
        "generate_practice",
        "explain_formula_error",
        "image_to_table",
        "excel_generate",
        "unknown",
    ]
    confidence: float = 0.0
    reason: str | None = None
