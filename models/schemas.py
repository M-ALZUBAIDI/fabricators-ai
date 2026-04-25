"""Pydantic data models and schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    question: str = Field(..., description="User question/message")
    session_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Session ID"
    )
    context: Optional[str] = Field(None, description="Additional context")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    session_id: str
    answer: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_used: str


class ConversationHistory(BaseModel):
    """Conversation history model."""

    session_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Design3DAsset(BaseModel):
    """3D asset model (embedded in JSON reports)."""

    format: str = Field(..., description="Format: 'gltf' or 'stl'")
    data_base64: str = Field(..., description="Binary file as base64 string")
    filename: str = Field(..., description="Original filename")
    size_bytes: int = Field(..., description="Original file size in bytes")


class DesignSpecification(BaseModel):
    """Design specification extracted from conversation."""

    description: str = Field(..., description="Design description")
    dimensions: Optional[Dict[str, float]] = Field(
        None, description="Dimensions (length, width, height, etc.)"
    )
    material: Optional[str] = Field(None, description="Suggested material")
    color: Optional[str] = Field(None, description="Color/finish")
    fabrication_method: Optional[str] = Field(
        None, description="Fabrication method (3D print, CNC, etc.)"
    )
    additional_notes: Optional[str] = Field(None)


class ReportData(BaseModel):
    """Report data model (embedded in JSON response)."""

    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Content
    conversation_summary: str = Field(..., description="Summary of conversation")
    design_specification: DesignSpecification
    key_points: List[str] = Field(default_factory=list)

    # 3D Assets (embedded as base64)
    assets_3d: List[Design3DAsset] = Field(default_factory=list)

    # Metadata
    conversation_length: int = Field(default=0, description="Number of exchanges")
    model_used: str = Field(default="unknown")

    # Shareable link info
    share_token: str = Field(default_factory=lambda: str(uuid.uuid4()))


class ReportRequest(BaseModel):
    """Request model for report generation."""

    session_id: str = Field(..., description="Session ID to generate report from")


class ReportResponse(BaseModel):
    """Response model for report endpoint."""

    report: ReportData
    pdf_available: bool = Field(False, description="Whether PDF export is available")


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy")
    version: str
    environment: str
    database_connected: bool
    llm_available: bool
