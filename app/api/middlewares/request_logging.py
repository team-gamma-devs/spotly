import time
import ipaddress
from fastapi import Request

from app.logger import get_logger

logger = get_logger(__name__)


async def log_requests_middleware(request: Request, call_next):
    """Middleware for logging incoming requests with real IP detection from ALB headers"""

    # Record the start time to calculate request processing time later
    start_time = time.time()

    # Default to "unknown" in case no valid IP is found
    real_ip = "unknown"

    # Attempt to get the real client IP from the ALB (Application Load Balancer) forwarded header
    x_forwarded_for = request.headers.get("X-Forwarded-For")

    if x_forwarded_for:
        # Take the first IP in the comma-separated list
        first_ip = x_forwarded_for.split(",")[0].strip()
        valid_ip = False
        try:
            # Validate IP format (IPv4 or IPv6)
            ipaddress.ip_address(first_ip)
            valid_ip = True
        except ValueError:
            valid_ip = False

        # If the IP is valid, use it as the real IP
        if valid_ip:
            real_ip = first_ip

    # Fallback: if no valid forwarded IP, use the direct client host from FastAPI
    if real_ip == "unknown" and request.client:
        real_ip = request.client.host

    # Get protocol from ALB forwarded header, default to "unknown"
    proto = request.headers.get("X-Forwarded-Proto", "unknown")

    # Log basic request information: method, path, client IP, and protocol
    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"IP: {real_ip} | Proto: {proto}"
    )

    # Call the next middleware or route handler
    response = await call_next(request)

    # Calculate total processing time for the request
    process_time = time.time() - start_time

    # Log response information: status code, processing time, and request path
    logger.info(
        f"Response: {response.status_code} | "
        f"Time: {process_time:.3f}s | "
        f"Path: {request.url.path}"
    )

    # Add a custom header to the response with the processing time
    response.headers["X-Process-Time"] = f"{process_time:.3f}"

    return response
