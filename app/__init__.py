from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.settings import settings
from app.logger import setup_logging, get_logger
from app.api.routes import api_router
from app.api.routes import health
from app.infrastructure.database.lifespan import lifespan
from app.api.middlewares.request_logging import log_requests_middleware
from app.api.middlewares.signature import verify_signature_and_origin
from app.api.middlewares.global_exceptions import global_exceptions_middleware
from app.api.middlewares.trusted_hosts import ConditionalTrustedHostMiddleware

setup_logging()
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
        docs_url=(
            "/docs" if settings.debug else None
        ),  # Disable docs in production
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # ============================================
    # MIDDLEWARES (order matters!)
    # ============================================

    # 1. Trusted Host Middleware (security)
    app.add_middleware(
        ConditionalTrustedHostMiddleware, allowed_hosts=settings.allowed_hosts
    )

    # 2. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    app.middleware("http")(log_requests_middleware)
    app.middleware("http")(verify_signature_and_origin)

    # GLOBAL EXCEPTION HANDLERS
    app.middleware("http")(global_exceptions_middleware)

    # INCLUDE ROUTERS
    app.include_router(api_router)
    app.include_router(health.router)

    logger.info(f"{settings.app_name} configured successfully")

    return app
