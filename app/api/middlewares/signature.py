from fastapi import Request, status
from fastapi.responses import JSONResponse

import hmac
import hashlib
import time

from app.logger import get_logger
from app.settings import settings

logger = get_logger(__name__)


PUBLIC_ROUTES = [
    "/health",
    "/health/ready",
    "/health/live",
]

# Documentation routes that should be accessible without signature
DOCS_ROUTES = [
    "/docs",
    "/redoc",
    "/openapi.json",
]


async def verify_signature_and_origin(request: Request, call_next):
    """
    Middleware to verify request authenticity by checking the origin and HMAC signature.

    Security checks:
        1. Verify that the request originates from the expected frontend (X-Frontend-Origin header).
        2. Verify that the request includes a valid HMAC signature (X-Signature) based on the payload and timestamp.
        3. Prevent replay attacks by validating that the timestamp is recent (within 5 minutes).

    Public routes (excluded from verification):
        - Health check endpoints (/health, etc.)
        - Documentation endpoints (/docs, /redoc, /openapi.json) - for local development

    Special handling:
        - For multipart/form-data requests, the signature is computed with an empty payload
          since the frontend cannot reliably reconstruct the multipart body for signing.

    Returns:
        - JSONResponse with 401 Unauthorized if any check fails.
        - Otherwise, forwards request to the next middleware or endpoint.

    Notes:
        - Assumes frontend_secret is configured in settings.
        - Logs all failed attempts with relevant IP and path information.
    """
    # Skip verification for public routes
    if request.url.path in PUBLIC_ROUTES:
        return await call_next(request)

    # Skip verification for documentation routes
    if (
        request.url.path in DOCS_ROUTES
        or request.url.path.startswith("/docs")
        or request.url.path.startswith("/redoc")
    ):
        return await call_next(request)

    frontend_secret = settings.frontend_secret

    # Get signature, origin and timestamp from headers
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

    # Verify signature and timestamp exist
    if not request_signature or not timestamp:
        logger.warning(
            f"Missing signature or timestamp from IP: {request.client.host if request.client else 'unknown'} | "
            f"Path: {request.url.path}"
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthorized: Missing authentication headers"},
        )

    # Verify timestamp is recent (prevent replay attacks)
    try:
        request_time = int(timestamp)
        current_time = int(time.time() * 1000)
        time_diff = abs(current_time - request_time)

        if time_diff > 300000:  # 5 minutes in milliseconds
            logger.warning(
                f"Expired timestamp from IP: {request.client.host if request.client else 'unknown'} | "
                f"Time diff: {time_diff}ms"
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

    # Check if request is multipart/form-data
    content_type = request.headers.get("Content-Type", "")
    is_multipart = content_type.startswith("multipart/form-data")

    if is_multipart:
        # For multipart requests, use empty payload (frontend sends empty body for signature)
        payload = ""
    else:
        # For regular requests, read and decode the body
        body = await request.body()
        payload = body.decode("utf-8") if body else ""

        # Restore the body for the next middleware/endpoint
        async def receive():
            return {"type": "http.request", "body": body}

        request._receive = receive

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
            f"Content-Type: {content_type} | "
            f"Expected: {expected_signature[:10]}... | Got: {request_signature[:10]}..."
        )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthorized: Invalid signature"},
        )

    # If validation passes, continue with request
    response = await call_next(request)
    return response
