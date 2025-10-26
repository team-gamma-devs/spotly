from fastapi import Request, status
from fastapi.responses import JSONResponse

import hmac
import hashlib
import time

from app.logger import get_logger
from app.settings import settings

logger = get_logger(__name__)


async def verify_signature_and_origin(request: Request, call_next):
    """
    Middleware to verify request authenticity by checking the origin and HMAC signature.

    Security checks:
        1. Verify that the request originates from the expected frontend (X-Frontend-Origin header).
        2. Verify that the request includes a valid HMAC signature (X-Signature) based on the payload and timestamp.
        3. Optional: Prevent replay attacks by validating that the timestamp is recent (within 5 minutes).

    Steps:
        - Extract headers: X-Frontend-Origin, X-Signature, and X-Timestamp.
        - Validate origin matches expected frontend.
        - Ensure signature and timestamp are present.
        - Reconstruct the message from timestamp and request body.
        - Compute HMAC using shared frontend secret and compare in constant time.
        - Validate timestamp is within allowed time window (prevent replay attacks).
        - Restore the request body for downstream middlewares or endpoints.

    Returns:
        - JSONResponse with 401 Unauthorized if any check fails.
        - Otherwise, forwards request to the next middleware or endpoint.

    Notes:
        - Assumes frontend_secret is configured in settings.
        - Logs all failed attempts with relevant IP and path information.
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

        if time_diff > 300000:  # 5 minutes in milliseconds
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
