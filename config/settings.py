"""Centralized configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings – populated from env vars or .env file."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Azure Document Intelligence
    azure_di_endpoint: str = Field(default="", description="Azure DI endpoint URL")
    azure_di_key: str = Field(default="", description="Azure DI API key")

    # Azure OpenAI (GPT-4o Vision)
    azure_openai_endpoint: str = Field(default="", description="Azure OpenAI endpoint")
    azure_openai_key: str = Field(default="", description="Azure OpenAI API key")
    azure_openai_deployment: str = Field(default="gpt-4o", description="Deployment name")
    azure_openai_api_version: str = Field(default="2024-12-01-preview")

    # Processing
    confidence_threshold: float = Field(
        default=0.85,
        description="Minimum confidence score before flagging for human review",
    )
    image_dpi: int = Field(default=300, description="DPI for PDF-to-image conversion")
    max_pages_per_call: int = Field(
        default=10,
        description="Maximum pages sent in a single LLM call",
    )
    log_level: str = Field(default="INFO")
    debug_artifacts_dir: str | None = Field(
        default=None,
        description="If set, intermediate images and prompts are saved here for debugging",
    )


def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
