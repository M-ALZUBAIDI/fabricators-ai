"""
Development environment settings.

For Google Colab testing and local development.
Uses lightweight/mock providers for fast iteration.
"""
import os
from config.settings import Settings


class DevelopmentSettings(Settings):
    """Development environment configuration."""

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # LLM Configuration (use mock for fast testing in Colab)
    LLM_PROVIDER: str = os.getenv("DEV_LLM_PROVIDER", "mock")
    MODEL_NAME: str = os.getenv("DEV_MODEL_NAME", "mock-model")
    MAX_TOKENS: int = int(os.getenv("DEV_MAX_TOKENS", "512"))
    TEMPERATURE: float = float(os.getenv("DEV_TEMPERATURE", "0.7"))

    # Features (disable expensive features in dev)
    GENERATION_3D_ENABLED: bool = True
    PDF_ENABLED: bool = False  # Disable PDF generation for speed

    # Database (use SQLite in dev)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./fabricators_dev.db"
    )

    # CORS (open in development)
    CORS_ORIGINS: list = ["*"]

    # Logging
    LOG_LEVEL: str = "debug"

