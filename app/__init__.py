from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time

from app.settings import settings
from app.logger import get_logger
from app.api import api_router
from app.api import health
from app.infrastructure.database.lifespan import lifespan

logger = get_logger(__name__)


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

    # INCLUDE ROUTERS
    app.include_router(api_router)
    app.include_router(health.router)

    # EXCEPTION HANDLERS
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

    logger.info(f"{settings.app_name} configured successfully")

    return app
