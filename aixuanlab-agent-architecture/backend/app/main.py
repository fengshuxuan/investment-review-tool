from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.ai_routes import router as ai_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(ai_router, prefix=settings.api_prefix)

# MVP local file serving. In production, prefer object storage or a protected download endpoint.
app.mount("/files", StaticFiles(directory=settings.generated_dir), name="files")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}
