from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

from app.logger import get_logger

logger = get_logger(__name__)


async def global_exceptions_middleware(request: Request, call_next):
    """
    Process the incoming request and handle exceptions.

    Args:
        request (Request): The incoming FastAPI request.
        call_next (Callable): The next request handler in the middleware stack.

    Returns:
        JSONResponse: Custom JSON response in case of errors or the normal response.
    """
    try:
        response = await call_next(request)
        if response.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Not Found",
                    "message": "The requested resource was not found",
                    "path": request.url.path,
                },
            )

        return response

    except (ValueError, TypeError) as e:
        logger.info(f"Error: {e}")

        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid data",
                "message": str(e),
                "path": request.url.path,
            },
        )

    except Exception as exc:
        # Unexpected errors: log full traceback
        logger.error(
            f"Unhandled exception: {exc}\n{traceback.format_exc()}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later.",
                "path": request.url.path,
            },
        )
