"""Configuration management for DevAgent."""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Literal


class Settings(BaseSettings):
    """Application settings."""

    # LLM Configuration
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: Literal["openai", "anthropic"] = "openai"
    llm_model: str = "gpt-4-turbo-preview"

    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    # Storage Configuration
    storage_path: Path = Path("./devagent/data/jobs")
    embeddings_path: Path = Path("./devagent/data/embeddings")
    fpdevsml_examples_path: Path = Path("./devagent/data/fpdevsml_examples")
    documentation_path: Path = Path("./devagent/data/documentation")

    # Retriever Configuration
    top_k_results: int = 5
    embedding_model: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
