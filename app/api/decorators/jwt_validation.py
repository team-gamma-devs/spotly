from fastapi import Request, HTTPException
from functools import wraps
from jose import jwt, JWTError
from typing import Callable, Any

from app.logger import get_logger
from app.settings import settings

logger = get_logger(__name__)


def require_jwt(for_manager: bool = False):
    """
    Decorator that validates a JWT (JSON Web Token) from the Authorization header.

    This decorator ensures that the request includes a valid JWT token. Optionally,
    it can enforce that the user has a manager role by setting `for_manager=True`.

    Args:
        for_manager (bool, optional): If True, the decorator will check that the
            user's role in the token's `user_metadata` is 'manager'. Defaults to False.

    Raises:
        RuntimeError: If the request object is not found in the endpoint parameters.
        HTTPException (403): If the token is missing, invalid, expired, or the user
            does not have the required manager role.

    Usage:
        @require_jwt()
        async def protected_endpoint(request: Request):
            # access the decoded JWT payload via request.state.user
            user_payload = request.state.user
            ...

        @require_jwt(for_manager=True)
        async def admin_endpoint(request: Request):
            # only accessible to users with role 'manager'
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Retrieve the Request object from kwargs or args
            request: Request = kwargs.get("request") or next(
                (a for a in args if isinstance(a, Request)), None
            )
            if request is None:
                raise RuntimeError(
                    "Request object not found. Add 'request: Request' to endpoint parameters."
                )

            # Extract the Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=403, detail="Token not provided")

            # Get the token part of the header
            token = auth_header.split(" ")[1]
            logger.info(f"Token: {token}")

            # Decode and validate the JWT
            try:
                payload = jwt.decode(
                    token,
                    settings.secret_key,
                    algorithms=[settings.algorithm],
                    audience="authenticated",
                )
                logger.info(f"payload: {payload}")
            except JWTError:
                raise HTTPException(status_code=403, detail="Invalid or expired token")

            # Store the decoded payload in request.state for later access
            request.state.user = payload
            logger.info(f"Request state: {request.__dict__}")

            # If manager access is required, check the user's role
            if for_manager:
                role = payload.get("user_metadata", {}).get("role", "").lower()
                if role != "manager":
                    raise HTTPException(status_code=403, detail="Admin access required")

            # Call the original endpoint function
            return await func(*args, **kwargs)

        return wrapper

    return decorator
