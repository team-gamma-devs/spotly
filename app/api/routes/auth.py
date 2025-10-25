from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.api.schemas.auth_schemas import LoginRequest, UserResponse
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
    response_model=UserResponse,
    response_model_by_alias=True,
)
async def auth_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    get_user = GetUser()

    try:
        user = await get_user.verify(token)
    except UserNotLoggedIn as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return user.to_dict()
