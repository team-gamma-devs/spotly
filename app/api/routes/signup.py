from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi import File, Form
from typing import Optional

from app.logger import get_logger
from app.services.use_cases.register_user.register_user import RegisterUser
from app.services.exceptions.register_user_exceptions import (
    FileTooLarge,
    InvalidFileType,
    InvalidCV,
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/sign-up",
    tags=["sign-up"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def sign_up(
    github_username: Optional[str] = Form(None),
    personal_cv: UploadFile = File(...),
    linkedin_cv: UploadFile = File(...),
    avatar_img: Optional[UploadFile] = File(None),
):

    if avatar_img and not avatar_img.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{avatar_img.filename} is not a valid image",
        )

    register_user = RegisterUser()
    try:
        registered_user = await register_user.register_user(personal_cv, linkedin_cv)
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
    except InvalidCV as e:
        logger.warning(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        )
    except Exception as e:
        logger.warning(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    return registered_user
