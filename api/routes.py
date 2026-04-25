"""FastAPI routes for the application."""
import logging
from fastapi import APIRouter, HTTPException, Query
from models import (
    ChatRequest,
    ChatResponse,
    ReportRequest,
    ReportResponse,
    HealthCheckResponse,
)
from utils.validators import validate_question, validate_session_id, ValidationError
from config import Settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

# These will be injected by the main app
chat_service = None
report_service = None
design_analyzer = None
three_d_generator = None
settings = None


def set_services(
    _chat_service, _report_service, _design_analyzer, _three_d_generator, _settings
):
    """Inject services into router."""
    global chat_service, report_service, design_analyzer, settings
    chat_service = _chat_service
    report_service = _report_service
    design_analyzer = _design_analyzer
    three_d_generator = _three_d_generator
    settings = _settings


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.ENVIRONMENT,
        database_connected=True,
        llm_available=True,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a chat message and get a response."""
    try:
        # Validate input
        validate_question(request.question)
        validate_session_id(request.session_id)

        logger.info(f"Chat request: session={request.session_id}")

        # Send message through chat service
        response = await chat_service.send_message(
            request.session_id, request.question
        )

        logger.info(f"Chat response generated for session: {request.session_id}")
        return response

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session."""
    try:
        validate_session_id(session_id)

        history = await chat_service.get_conversation_history(session_id)
        if not history:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"session_id": session_id, "messages": history.messages}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """Generate a report from conversation."""
    try:
        validate_session_id(request.session_id)

        logger.info(f"Report generation requested for session: {request.session_id}")

        # Check if 3D generation is enabled
        if settings.GENERATION_3D_ENABLED:
            try:
                # Generate default cube as example
                assets_3d = await three_d_generator.generate_cube(
                    size=100, include_formats=["gltf", "stl"]
                )
            except Exception as e:
                logger.warning(f"3D generation failed: {e}")
                assets_3d = []
        else:
            assets_3d = []

        # Generate report
        report = await report_service.generate_report(
            request.session_id, assets_3d=assets_3d
        )

        logger.info(f"Report generated: {report.report_id}")

        return ReportResponse(
            report=report,
            pdf_available=settings.PDF_ENABLED,
        )

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/report/{report_id}")
async def get_report(report_id: str):
    """Retrieve a stored report."""
    try:
        validate_session_id(report_id)  # Use for general validation

        report = report_service.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        return {"report": report}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/report/{report_id}/export-pdf")
async def export_report_pdf(report_id: str):
    """Export report as PDF."""
    try:
        if not settings.PDF_ENABLED:
            raise HTTPException(status_code=503, detail="PDF export not enabled")

        validate_session_id(report_id)

        pdf_bytes = await report_service.export_report_to_pdf(report_id)

        return {
            "status": "success",
            "message": "PDF exported successfully",
            "size_bytes": len(pdf_bytes),
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/3d/generate")
async def generate_3d_asset(
    shape: str = Query("cube", description="Shape type: cube, cylinder, sphere"),
    size: float = Query(100, description="Size parameter"),
    formats: list = Query(
        ["gltf", "stl"], description="Formats to generate"
    ),
):
    """Generate a 3D asset."""
    try:
        if not settings.GENERATION_3D_ENABLED:
            raise HTTPException(status_code=503, detail="3D generation not enabled")

        logger.info(f"3D asset generation: shape={shape}, size={size}")

        # Generate based on shape
        if shape.lower() == "cube":
            assets = await three_d_generator.generate_cube(size, formats)
        elif shape.lower() == "cylinder":
            assets = await three_d_generator.generate_cylinder(
                radius=size / 2, height=size, include_formats=formats
            )
        elif shape.lower() == "sphere":
            assets = await three_d_generator.generate_sphere(size / 2, formats)
        else:
            raise HTTPException(status_code=400, detail="Unknown shape type")

        logger.info(f"Generated {len(assets)} 3D assets")

        return {
            "status": "success",
            "assets": assets,
            "count": len(assets),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating 3D asset: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
