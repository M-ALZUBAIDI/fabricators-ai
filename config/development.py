"""Development environment settings."""
from config.settings import Settings


class DevelopmentSettings(Settings):
    """Development environment configuration."""

    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./fabricators_dev.db"
    LLM_PROVIDER: str = "mock"  # Use mock for fast dev testing
    GENERATION_3D_ENABLED: bool = True
    PDF_ENABLED: bool = False  # Disable PDF in dev for speed
