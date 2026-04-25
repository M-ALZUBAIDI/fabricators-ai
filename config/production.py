"""Production environment settings."""
from config.settings import Settings


class ProductionSettings(Settings):
    """Production environment configuration."""

    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql://user:password@localhost/fabricators_prod"
    LLM_PROVIDER: str = "unsloth"  # Use real Unsloth models
    GENERATION_3D_ENABLED: bool = True
    PDF_ENABLED: bool = True
