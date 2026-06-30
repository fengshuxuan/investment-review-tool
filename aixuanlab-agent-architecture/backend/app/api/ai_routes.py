from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.schemas.ai import (
    ChatRequest,
    ChatResponse,
    ExcelGenerateRequest,
    ExcelGenerateResponse,
    FormulaErrorRequest,
    FormulaErrorResponse,
    GeneratePracticeRequest,
    PracticeQuestion,
    TableRecognitionResponse,
)
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.excel_service import ExcelService
from app.services.image_table_service import ImageTableService

router = APIRouter(prefix="/ai", tags=["AI Agent"])


def get_current_user_id() -> str:
    """MVP placeholder.

    Production rule:
    - Resolve user_id from JWT/session/auth middleware.
    - Never trust user_id from request body.
    """
    return "demo-user"


def get_agent() -> AgentOrchestrator:
    return AgentOrchestrator()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    agent: AgentOrchestrator = Depends(get_agent),
) -> ChatResponse:
    return agent.chat(user_id, request)


@router.post("/generate-practice", response_model=PracticeQuestion)
def generate_practice(
    request: GeneratePracticeRequest,
    user_id: str = Depends(get_current_user_id),
    agent: AgentOrchestrator = Depends(get_agent),
) -> PracticeQuestion:
    return agent.generate_practice(user_id, request)


@router.post("/explain-formula-error", response_model=FormulaErrorResponse)
def explain_formula_error(
    request: FormulaErrorRequest,
    user_id: str = Depends(get_current_user_id),
    agent: AgentOrchestrator = Depends(get_agent),
) -> FormulaErrorResponse:
    return agent.explain_formula_error(user_id, request)


@router.post("/excel/generate", response_model=ExcelGenerateResponse)
def generate_excel(
    request: ExcelGenerateRequest,
    user_id: str = Depends(get_current_user_id),
) -> ExcelGenerateResponse:
    service = ExcelService()
    return service.generate_practice_workbook(
        user_id=user_id,
        practice=request.practice,
        include_answer_sheet=request.include_answer_sheet,
    )


@router.post("/image-to-table", response_model=TableRecognitionResponse)
def image_to_table(
    image_url: str = Form(...),
    user_id: str = Depends(get_current_user_id),
) -> TableRecognitionResponse:
    # MVP accepts an image_url. Later add UploadFile storage and signed public URL generation.
    service = ImageTableService()
    return service.recognize_table_from_url(image_url)


@router.post("/upload-image-placeholder")
def upload_image_placeholder(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
) -> dict:
    return {
        "message": "TODO: save file under uploads/{user_id}/{file_id} and return a public/signed URL for Ark vision call.",
        "filename": file.filename,
        "user_id": user_id,
    }
