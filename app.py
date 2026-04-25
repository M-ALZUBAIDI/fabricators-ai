"""Main FastAPI application."""
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
environment = os.getenv("ENVIRONMENT", "development")
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

    logger.info("Application starting...")

    try:
        # Initialize LLM provider
        llm_provider = LLMProviderFactory.create(
            provider_type=settings.LLM_PROVIDER,
            model_name=settings.MODEL_NAME,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
        )
        await llm_provider.initialize()

        # Initialize services
        chat_service = ChatService(llm_provider)
        design_analyzer = DesignAnalyzerService(llm_provider)
        three_d_generator = ThreeDGeneratorService()
        report_service = ReportService(llm_provider, chat_service, design_analyzer)

        # Inject services into routes
        set_services(chat_service, report_service, design_analyzer, three_d_generator, settings)

        logger.info("Application initialized successfully")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Application shutting down...")
    if llm_provider:
        await llm_provider.shutdown()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered fabrication platform",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(logging_middleware)
app.middleware("http")(error_handler_middleware)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
