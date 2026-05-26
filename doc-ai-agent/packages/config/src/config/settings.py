from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to *this file* so the correct file is loaded
# regardless of which directory the process is launched from.
#
# File layout:
#   doc-ai-agent/           ← workspace root  (5 levels up from here)
#     .env
#     packages/
#       config/
#         src/
#           config/
#             settings.py   ← __file__
_THIS_FILE = Path(__file__).resolve()
_WORKSPACE_ROOT = _THIS_FILE.parent.parent.parent.parent.parent
_ENV_FILE = _WORKSPACE_ROOT / ".env"

# Fallback to CWD/.env in case the layout changes or the file is missing
_ENV_PATH = str(_ENV_FILE) if _ENV_FILE.exists() else ".env"


class Settings(BaseSettings):
    """
    env vars are loaded automatically from .env file in the project root
    model_config uses pydantic settings to automatically load and map envs to the class attributes

    Anything passed as parameter to the constructor pydantic considers it as highest priority
    and overrides any env var with the same name
    """

    model_config = SettingsConfigDict(
        env_file=_ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    service_name: str = "service"
    environment: str = "development"
    log_level: str = "INFO"
    log_format: str = "json" 
    database_url: str = "postgresql://postgres:postgres@localhost:5432/doc_ai"
    ollama_host: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text"
    

    # Routing thresholds and parameters
    auto_assign_threshold: float = 0.7
    review_threshold: float = 0.4
    top_k: int = 4

    #LLM settings
    google_api_key: str 
    agent_model: str ="gemini-2.5-flash"
    finger_print_model: str = "gemini-2.5-flash"
    groq_api_key:str

    # GitHub settings
    github_api_url: str
    github_org: str
    github_repo: str
    github_base_path: str
    github_token: str

    # RabbitMQ settings
    rabbitmq_url: str
    rabbitmq_queue: str


@lru_cache
def get_settings(service_name: str | None = None) -> Settings:
    overrides: dict[str, str] = {}
    if service_name:
        overrides["service_name"] = service_name
    """
    ** unpack and pass the arguments to settings
    """
    return Settings(**overrides)

