"""API middleware."""
import logging
import time
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # Calculate process time
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} (took {process_time:.3f}s)")

    return response


async def error_handler_middleware(request: Request, call_next):
    """Handle errors gracefully."""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
