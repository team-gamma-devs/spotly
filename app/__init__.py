from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.settings import settings
from app.api import api_router
from app.database import connect_to_mongo, close_mongo_connection

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Replaces deprecated @app.on_event decorators.
    """
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} in {settings.app_env} mode...")

    try:
        # Connect to MongoDB
        await connect_to_mongo()
        logger.info("✅ Application startup complete")

        yield  # Application is running

    finally:
        # Shutdown
        logger.info(f"🛑 Shutting down {settings.app_name}...")
        await close_mongo_connection()
        logger.info("✅ Application shutdown complete")


def create_app() -> FastAPI:
    """
    Application factory pattern for creating FastAPI instances.
    Returns a production-ready configured app.
    """

    app = FastAPI(
        title=settings.app_name,
        description="API for Spotly - Production Ready",
        version="1.0.0",
        debug=settings.debug,
        docs_url="/docs" if settings.debug else None,  # Disable docs in production
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # ============================================
    # MIDDLEWARES (order matters!)
    # ============================================

    # 1. Trusted Host Middleware (security)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

    # 2. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # 4. Request logging and timing middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()

        # Get real IP from nginx headers
        real_ip = request.headers.get(
            "X-Real-IP", request.client.host if request.client else "unknown"
        )

        # Log request
        logger.info(f"Request: {request.method} {request.url.path} from {real_ip}")

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {response.status_code} | "
            f"Time: {process_time:.3f}s | "
            f"Path: {request.url.path}"
        )

        # Add custom header with processing time
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        return response

    # ============================================
    # HEALTH CHECK ENDPOINTS
    # ============================================

    @app.get("/health", tags=["Health"], include_in_schema=False)
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

    @app.get("/health/ready", tags=["Health"], include_in_schema=False)
    async def readiness_check():
        """
        Readiness probe - checks if app is ready to receive traffic.
        Verifies database connections, etc.
        """
        try:
            from app.database import db

            # Verify MongoDB connection
            await db.client.admin.command("ping")

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

    @app.get("/health/live", tags=["Health"], include_in_schema=False)
    async def liveness_check():
        """
        Liveness probe - checks if app is alive (not hung).
        """
        return {"status": "alive"}

    # ============================================
    # ROOT ENDPOINT (for testing)
    # ============================================

    @app.get("/", tags=["Root"])
    async def root(request: Request):
        """
        Root endpoint - shows API info and nginx headers (useful for debugging).
        """
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": "1.0.0",
            "environment": settings.app_env,
            "docs": "/docs" if settings.debug else "disabled in production",
            "headers": (
                {
                    "host": request.headers.get("host"),
                    "x-real-ip": request.headers.get("x-real-ip"),
                    "x-forwarded-for": request.headers.get("x-forwarded-for"),
                    "x-forwarded-proto": request.headers.get("x-forwarded-proto"),
                }
                if settings.debug
                else "hidden in production"
            ),
        }

    # ============================================
    # INCLUDE ROUTERS
    # ============================================

    app.include_router(api_router)

    # ============================================
    # EXCEPTION HANDLERS
    # ============================================

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": "The requested resource was not found",
                "path": request.url.path,
            },
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        logger.error(f"Internal server error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later.",
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred.",
            },
        )

    logger.info(f"✅ {settings.app_name} configured successfully")

    return app
