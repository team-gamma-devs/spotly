from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.api.schemas.auth_schemas import LoginRequest, LoginResponse
from app.services.user_login.user_login import AuthUser
from app.services.user_login.exceptions import UserNotRegistered


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def login(payload: LoginRequest):
    email = payload.email
    verify_user = AuthUser()

    try:
        token = await verify_user.execute(email)
    except UserNotRegistered as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    return {
        "message": "Logged Successfully",
        "access_token": token,
        "token_type": "bearer",
    }
