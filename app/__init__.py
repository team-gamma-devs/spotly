from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import ipaddress
import hmac
import hashlib

from app.settings import settings
from app.logger import setup_logging, get_logger
from app.api.routes import api_router
from app.api.routes import health
from app.infrastructure.database.lifespan import lifespan

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

        # Get real IP from ALB headers with validation
        real_ip = "unknown"
        x_forwarded_for = request.headers.get("X-Forwarded-For")

        if x_forwarded_for:
            first_ip = x_forwarded_for.split(",")[0].strip()
            valid_ip = False
            try:
                ipaddress.ip_address(first_ip)
                valid_ip = True
            except ValueError:
                valid_ip = False
            # Validate IP format (basic validation)
            if valid_ip:
                real_ip = first_ip

        # Fallback to direct client host if no valid forwarded IP
        if real_ip == "unknown" and request.client:
            real_ip = request.client.host

        # Log request with additional ALB headers
        proto = request.headers.get("X-Forwarded-Proto", "unknown")
        logger.info(
            f"Request: {request.method} {request.url.path} | "
            f"IP: {real_ip} | Proto: {proto}"
        )

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

    @app.middleware("http")
    async def verify_signature_and_origin(request: Request, call_next):
        """
        Middleware to verify request signature and origin.
        Only allows requests from vercel-spotly client with valid HMAC signature.
        """
        frontend_secret = settings.frontend_secret

        # Get signature, origin and message from headers
        request_signature = request.headers.get("X-Signature")
        request_origin = request.headers.get("X-Frontend-Origin")
        timestamp = request.headers.get("X-Timestamp")

        # Verify origin
        if not request_origin or request_origin != "vercel-spotly-client":
            logger.warning(
                f"Invalid origin: {request_origin} from IP: {request.client.host if request.client else 'unknown'} | "
                f"Path: {request.url.path}"
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Unauthorized: Invalid origin"},
            )

        # Verify signature exists
        if not request_signature or not timestamp:
            logger.warning(
                f"Missing signature or message from IP: {request.client.host if request.client else 'unknown'} | "
                f"Path: {request.url.path}"
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Unauthorized: Missing authentication headers"},
            )

        body = await request.body()
        payload = body.decode("utf-8") if body else ""

        # Reconstruct the message: timestamp:payload
        message = f"{timestamp}:{payload}"

        # Generate HMAC on backend
        expected_signature = hmac.new(
            key=frontend_secret.encode("utf-8"),
            msg=message.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        # Compare signatures using constant-time comparison
        if not hmac.compare_digest(request_signature, expected_signature):
            logger.warning(
                f"Invalid signature from IP: {request.client.host if request.client else 'unknown'} | "
                f"Path: {request.url.path} | "
                f"Expected: {expected_signature[:10]}... | Got: {request_signature[:10]}..."
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Unauthorized: Invalid signature"},
            )

        # Optional: Verify timestamp is recent (prevent replay attacks)
        try:
            request_time = int(timestamp)
            current_time = int(time.time() * 1000)
            time_diff = abs(current_time - request_time)

            if time_diff > 300000:
                logger.warning(
                    f"Expired timestamp from IP: {request.client.host if request.client else 'unknown'}"
                )
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Unauthorized: Request expired"},
                )
        except ValueError:
            logger.warning(
                f"Invalid timestamp format from IP: {request.client.host if request.client else 'unknown'}"
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Unauthorized: Invalid timestamp"},
            )

        # Restore the body for the next middleware/endpoint
        async def receive():
            return {"type": "http.request", "body": body}

        request._receive = receive

        # If validation passes, continue with request
        response = await call_next(request)
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
