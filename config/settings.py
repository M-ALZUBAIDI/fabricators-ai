"""Base configuration settings."""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Base settings for all environments."""

    # App
    APP_NAME: str = "Fabricators AI"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "production"] = "production"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./fabricators.db"

    # LLM Provider (Unsloth only)
    LLM_PROVIDER: str = "unsloth"
    MODEL_NAME: str = "meta-llama/Llama-2-7b-hf"
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.7

    # 3D Generation
    GENERATION_3D_ENABLED: bool = True
    PRIMARY_3D_FORMAT: str = "gltf"
    SECONDARY_3D_FORMAT: str = "stl"

    # Report Generation
    PDF_ENABLED: bool = True
    INCLUDE_3D_PREVIEW_IN_PDF: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings() -> Settings:
    """Get settings based on environment."""
    return Settings()
