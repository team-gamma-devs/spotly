from fastapi import Request, HTTPException
from functools import wraps
from jose import jwt, JWTError
from typing import Callable, Any
import logging

from app.settings import settings

logger = logging.getLogger(__name__)


def require_jwt(for_manager: bool = False):
    """
    Decorator that validates JWT tokens.
    Optionally checks if user is admin if `for_admin=True`.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            request: Request = kwargs.get("request") or next(
                (a for a in args if isinstance(a, Request)), None
            )
            if request is None:
                raise RuntimeError(
                    "Request object not found. Add 'request: Request' to endpoint parameters."
                )

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=403, detail="Token not provided")

            token = auth_header.split(" ")[1]
            logger.info(f"Token: {token}")

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

            # Guardar info del usuario en el request
            request.state.user = payload
            logger.info(f"Request: {request.__dict__}")

            # Check de rol admin si se requiere
            if for_manager:
                role = payload.get("user_metadata", {}).get("role", "").lower()
                if role != "manager":
                    raise HTTPException(status_code=403, detail="Admin access required")

            return await func(*args, **kwargs)

        return wrapper

    return decorator
