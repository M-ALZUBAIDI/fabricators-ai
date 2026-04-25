"""
Production environment settings.

LOCKED CONFIGURATION - Read from .env.production
These are the settings used when deploying to production.
"""
import os
from config.settings import Settings


class ProductionSettings(Settings):
    """Production environment configuration."""

    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # LLM Configuration (locked based on testing results)
    LLM_PROVIDER: str = os.getenv("PROD_LLM_PROVIDER", "unsloth")
    MODEL_NAME: str = os.getenv("PROD_MODEL_NAME", "meta-llama/Llama-2-7b-hf")
    MAX_TOKENS: int = int(os.getenv("PROD_MAX_TOKENS", "512"))
    TEMPERATURE: float = float(os.getenv("PROD_TEMPERATURE", "0.7"))

    # Features (enable for production)
    GENERATION_3D_ENABLED: bool = True
    PDF_ENABLED: bool = True

    # Database (use PostgreSQL in production)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost/fabricators_prod"
    )

    # CORS (restrict in production)
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000"
    ).split(",")

    # Logging
    LOG_LEVEL: str = "info"

