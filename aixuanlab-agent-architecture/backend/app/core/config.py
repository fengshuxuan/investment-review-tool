from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "aixuanlab-ai-agent"
    app_env: str = "development"
    api_prefix: str = "/api"

    ark_api_key: str = ""
    ark_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    ark_model: str = "doubao-seed-2-1-pro-260628"

    database_url: str = "sqlite:///./aixuanlab_agent.db"
    upload_dir: str = "./uploads"
    generated_dir: str = "./generated"
    public_file_base_url: str = "http://localhost:8000/files"

    auth_required: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
