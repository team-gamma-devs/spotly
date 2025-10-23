import time
import ipaddress
from fastapi import Request
import logging

logger = logging.getLogger(__name__)


async def log_requests_middleware(request: Request, call_next):
    """Middleware para logging de requests con información de IP real desde ALB"""
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
