"""Input validation utilities."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""

    pass


def validate_question(question: str, min_length: int = 3, max_length: int = 1000) -> bool:
    """Validate user question."""
    if not question:
        raise ValidationError("Question cannot be empty")

    if len(question) < min_length:
        raise ValidationError(f"Question must be at least {min_length} characters")

    if len(question) > max_length:
        raise ValidationError(f"Question cannot exceed {max_length} characters")

    return True


def validate_session_id(session_id: str) -> bool:
    """Validate session ID format."""
    if not session_id:
        raise ValidationError("Session ID cannot be empty")

    # UUID format validation
    if len(session_id) != 36:  # UUID format
        logger.warning(f"Session ID format unusual: {session_id}")

    return True


def validate_report_id(report_id: str) -> bool:
    """Validate report ID format."""
    if not report_id:
        raise ValidationError("Report ID cannot be empty")

    return True


def validate_3d_dimensions(
    width: float = None,
    height: float = None,
    depth: float = None,
    min_size: float = 1,
    max_size: float = 10000,
) -> bool:
    """Validate 3D dimensions."""
    dimensions = [d for d in [width, height, depth] if d is not None]

    for dim in dimensions:
        if not isinstance(dim, (int, float)):
            raise ValidationError("Dimensions must be numeric")

        if dim < min_size:
            raise ValidationError(f"Dimensions must be at least {min_size}")

        if dim > max_size:
            raise ValidationError(f"Dimensions cannot exceed {max_size}")

    return True
