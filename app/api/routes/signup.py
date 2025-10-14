from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi import File, Query, Form

from app.logger import get_logger
from app.services.register_user.register_user import RegisterUser
from app.services.register_user.exceptions import InvitationNotFound, InvitationExpired

logger = get_logger(__name__)

router = APIRouter(
    prefix="/sign-up",
    tags=["sign-up"],
)


@router.get("/invite", status_code=status.HTTP_200_OK)
async def check_invitation_token(token: str = Query(...)):
    token_validations = RegisterUser()
    try:
        token_state = await token_validations.check_invitation(token)
        logger.info(f"Token '{token}' checked successfully: {token_state}")
    except InvitationNotFound as e:
        logger.warning(f"Token '{token}' not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvitationExpired as e:
        logger.info(f"Token '{token}' expired")
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(e))

    return {"token_state": token_state}


@router.post("/", status_code=202)
async def sign_up(
    token: str = Query(...),
    github_username: str = Form(...),
    personal_cv: UploadFile = File(...),
    linkedin_cv: UploadFile = File(...),
    avatar_img: UploadFile = File(...),
):

    for file in [personal_cv, linkedin_cv]:
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400, detail=f"{file.filename} is not valid PDF"
            )

    if not avatar_img.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail=f"{avatar_img.filename} is not a valid image"
        )
