from fastapi import Request, HTTPException
from functools import wraps
from jose import jwt, JWTError
from typing import Callable, Any

from app.settings import settings


def require_jwt(for_admin: bool = False):
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

            try:
                payload = jwt.decode(
                    token, settings.secret_key, algorithms=[settings.algorithm]
                )
            except JWTError:
                raise HTTPException(status_code=403, detail="Invalid or expired token")

            # Guardar info del usuario en el request
            request.state.user = payload

            # Check de rol admin si se requiere
            if for_admin and not payload.get("is_admin", False):
                raise HTTPException(status_code=403, detail="Admin access required")

            return await func(*args, **kwargs)

        return wrapper

    return decorator
