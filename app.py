"""
Fabricators AI - Production Application

This is the PRODUCTION application. No testing code here.
Use this to run the actual service locally or on a server.

For testing/development: Use Google Colab (see TESTING.md)
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Settings, get_settings
from utils.logger import setup_logging
from models.llm_provider import LLMProviderFactory
from services import ChatService, DesignAnalyzerService, ReportService, ThreeDGeneratorService
from api.routes import router, set_services
from api.middleware import logging_middleware, error_handler_middleware

# Setup logging
environment = os.getenv("ENVIRONMENT", "production")
logger = setup_logging(environment)
settings = get_settings()

# Global service instances
llm_provider = None
chat_service = None
design_analyzer = None
report_service = None
three_d_generator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI."""
    global llm_provider, chat_service, design_analyzer, report_service, three_d_generator

    logger.info(f"[{settings.ENVIRONMENT.upper()}] Application starting...")

    try:
        # Initialize LLM provider with production settings
        llm_provider = LLMProviderFactory.create(
            provider_type=settings.LLM_PROVIDER,
            model_name=settings.MODEL_NAME,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
        )
        await llm_provider.initialize()

        # Initialize all services
        chat_service = ChatService(llm_provider)
        design_analyzer = DesignAnalyzerService(llm_provider)
        three_d_generator = ThreeDGeneratorService()
        report_service = ReportService(llm_provider, chat_service, design_analyzer)

        # Inject services into routes
        set_services(chat_service, report_service, design_analyzer, three_d_generator, settings)

        logger.info(f"✓ Application initialized successfully")
        logger.info(f"  Environment: {settings.ENVIRONMENT}")
        logger.info(f"  LLM Provider: {settings.LLM_PROVIDER}")
        logger.info(f"  Model: {settings.MODEL_NAME}")

    except Exception as e:
        logger.error(f"✗ Failed to initialize application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Application shutting down...")
    if llm_provider:
        await llm_provider.shutdown()
    logger.info("✓ Application shutdown complete")


# Create FastAPI app with production configuration
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered fabrication platform",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add CORS middleware (configure based on environment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if hasattr(settings, "CORS_ORIGINS") else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(logging_middleware)
app.middleware("http")(error_handler_middleware)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    # Production app - DO NOT use reload in production
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # Always False in production
        log_level="info" if settings.DEBUG else "warning",
    )
