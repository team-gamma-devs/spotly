from fastapi import APIRouter, UploadFile, HTTPException, status, Request
from fastapi import File, Form
from typing import Optional

from app.logger import get_logger
from app.api.decorators.jwt_validation import require_jwt
from app.services.use_cases.register_user.register_user import RegisterUser
from app.services.exceptions.register_user_exceptions import (
    FileTooLarge,
    InvalidFileType,
    InvalidCV,
)
from app.infrastructure.ai.exceptions import ParsingError, ServiceLimitError

logger = get_logger(__name__)

router = APIRouter(
    prefix="/sign-up",
    tags=["sign-up"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
@require_jwt()
async def sign_up(
    request: Request,
    github_username: Optional[str] = Form(None),
    personal_cv: UploadFile = File(...),
    linkedin_cv: UploadFile = File(...),
    avatar_img: UploadFile = File(...),
):
    email = request.state.user.get("email")
    register_user = RegisterUser()
    try:
        registered_user = await register_user.register_user(
            personal_cv, linkedin_cv, avatar_img, github_username, email
        )
    except FileTooLarge as e:
        logger.warning(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=str(e)
        )
    except InvalidFileType as e:
        logger.warning(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e)
        )
    except (InvalidCV, ParsingError) as e:
        logger.warning(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        )
    except ServiceLimitError as e:
        logger.warning(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e)
        )

    return registered_user
