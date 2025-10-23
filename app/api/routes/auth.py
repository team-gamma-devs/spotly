from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.api.schemas.auth_schemas import LoginRequest, LoginResponse, UserResponse
from app.services.use_cases.user_login import UserLogin
from app.services.use_cases.get_user import GetUser
from app.services.exceptions.user_login_exceptions import (
    InvitationExpired,
    InvitationNotFound,
)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

security = HTTPBearer()


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    response_model_by_alias=True,
)
async def login(payload: LoginRequest):
    email = payload.email
    user_login = UserLogin()

    try:
        login_data = await user_login.login(email)
    except InvitationNotFound as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvitationExpired as e:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(e))

    return {
        "message": "Logged Successfully",
        "access_token": login_data["token"],
        "token_type": "bearer",
        "role": login_data["role"],
        "is_first_time": login_data["is_first_time"],
    }


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
    except UserNotRegistered as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return user.to_dict()
