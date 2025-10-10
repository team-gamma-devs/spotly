from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.settings import settings
from app.logger import get_logger
from app.infrastructure.database import MongoDB

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health", tags=["Health"], include_in_schema=False)
async def health_check():
    """
    Basic health check for nginx, docker, and kubernetes.
    No authentication required.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.app_env,
    }


@router.get("/health/ready", tags=["Health"], include_in_schema=False)
async def readiness_check():
    """
    Readiness probe - checks if app is ready to receive traffic.
    Verifies database connections, etc.
    """
    try:
        # Verify MongoDB connection
        await MongoDB.client.command("ping")

        return {
            "status": "ready",
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "disconnected",
                "error": str(e),
            },
        )


@router.get("/health/live", tags=["Health"], include_in_schema=False)
async def liveness_check():
    """
    Liveness probe - checks if app is alive (not hung).
    """
    return {"status": "alive"}


# ============================================
# ROOT ENDPOINT (for testing)
# ============================================


@router.get("/", tags=["Root"])
async def root(request: Request):
    """
    Root endpoint - shows API info and ALB headers (useful for debugging).
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": "1.0.0",
        "environment": settings.app_env,
        "docs": "/docs" if settings.debug else "disabled in production",
        "headers": (
            {
                "host": request.headers.get("host"),
                "x-forwarded-for": request.headers.get("x-forwarded-for"),
                "x-forwarded-proto": request.headers.get("x-forwarded-proto"),
                "x-forwarded-port": request.headers.get("x-forwarded-port"),
                "x-amzn-trace-id": request.headers.get(
                    "x-amzn-trace-id"
                ),  # Specific to AWS
                "user-agent": request.headers.get("user-agent"),
            }
            if settings.debug
            else "hidden in production"
        ),
    }
