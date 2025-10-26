from fastapi import APIRouter, HTTPException, status, Request
from fastapi.security import HTTPBearer

from app.api.decorators.jwt_validation import require_jwt
from app.api.schemas.auth_schemas import LoginRequest, UserMe
from app.infrastructure.supabase import supabase_client
from app.services.use_cases.user_login import UserLogin
from app.services.use_cases.get_user import GetUser
from app.services.exceptions.user_login_exceptions import (
    InvitationExpired,
    InvitationNotFound,
    UserNotLoggedIn,
)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

security = HTTPBearer()


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def login(payload: LoginRequest):
    email = payload.email
    user_login = UserLogin()

    try:
        await user_login.login(email)
    except InvitationNotFound as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvitationExpired as e:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(e))

    return {f"message": "Magic link sent to {email}"}


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserMe,
    response_model_exclude_none=True,
    response_model_by_alias=True,
)
@require_jwt()
async def auth_me(request: Request):
    get_user = GetUser()

    try:
        user_data = await get_user.verify(request.state.user)
    except UserNotLoggedIn as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return user_data
