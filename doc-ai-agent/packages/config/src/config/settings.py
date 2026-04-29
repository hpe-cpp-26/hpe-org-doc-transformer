from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    env vars are loaded automatically from .env file in the project root
    model_config uses pydantic settings to automatically load and map envs to the class attributes

    Anything passed as parameter to the constructor pydantic considers it as highest priority
    and overrides any env var with the same name
    """

    model_config = SettingsConfigDict(
        env_file=".env",
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


@lru_cache
def get_settings(service_name: str | None = None) -> Settings:
    overrides: dict[str, str] = {}
    if service_name:
        overrides["service_name"] = service_name
    """
    ** unpack and pass the arguments to settings
    """
    return Settings(**overrides)

