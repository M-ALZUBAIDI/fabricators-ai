"""Pytest configuration and fixtures."""
import pytest
import asyncio
from pytest_asyncio import fixture
from config import Settings
from models.llm_provider import MockProvider
from services import ChatService, DesignAnalyzerService, ReportService, ThreeDGeneratorService


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@fixture
async def mock_llm_provider():
    """Create mock LLM provider."""
    provider = MockProvider()
    await provider.initialize()
    yield provider
    await provider.shutdown()


@fixture
async def chat_service(mock_llm_provider):
    """Create chat service with mock provider."""
    return ChatService(mock_llm_provider)


@fixture
async def design_analyzer(mock_llm_provider):
    """Create design analyzer with mock provider."""
    return DesignAnalyzerService(mock_llm_provider)


@fixture
async def three_d_generator_service():
    """Create 3D generator service."""
    return ThreeDGeneratorService()


@fixture
async def report_service(mock_llm_provider, chat_service, design_analyzer):
    """Create report service."""
    return ReportService(mock_llm_provider, chat_service, design_analyzer)


@pytest.fixture
def test_settings():
    """Create test settings."""
    return Settings(
        ENVIRONMENT="testing",
        DEBUG=True,
        DATABASE_URL="sqlite:///./test.db",
        LLM_PROVIDER="mock",
    )
