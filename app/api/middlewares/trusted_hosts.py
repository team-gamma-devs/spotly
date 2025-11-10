from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers
from starlette.responses import PlainTextResponse


class ConditionalTrustedHostMiddleware(BaseHTTPMiddleware):
    """
    Custom middleware that applies TrustedHost validation
    but excludes specific public routes like health checks.
    """

    # Rutas públicas que no requieren validación de host
    PUBLIC_ROUTES = [
        "/health",
        "/health/ready",
        "/health/live",
    ]

    def __init__(self, app, allowed_hosts=None):
        super().__init__(app)
        self.allowed_hosts = allowed_hosts or ["*"]

    async def dispatch(self, request, call_next):
        # Skip host validation for public routes
        if request.url.path in self.PUBLIC_ROUTES:
            return await call_next(request)

        # Apply TrustedHost validation for all other routes
        headers = Headers(scope=request.scope)
        host = headers.get("host", "").split(":")[0]

        # If allowed_hosts contains "*", allow all hosts
        if "*" in self.allowed_hosts:
            return await call_next(request)

        # Check if host is in allowed list
        if host not in self.allowed_hosts:
            # Check for wildcard domains (e.g., "*.example.com")
            allowed = False
            for pattern in self.allowed_hosts:
                if pattern.startswith("*."):
                    # Wildcard subdomain matching
                    domain = pattern[2:]
                    if host.endswith(domain):
                        allowed = True
                        break

            if not allowed:
                return PlainTextResponse("Invalid host header", status_code=400)

        return await call_next(request)
