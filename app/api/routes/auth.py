from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime

from app.api.schemas.auth_schemas import LoginRequest, LoginResponse, UserResponse
from app.services.use_cases.user_login import AuthUser
from app.services.use_cases.get_user import GetUser
from app.services.exceptions.user_login_exceptions import UserNotRegistered


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

security = HTTPBearer()


@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
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


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def auth_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    get_user = GetUser()

    try:
        user = await get_user.execute(token)
    except UserNotRegistered as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    admin = {
        "first_name": "Laura",
        "last_name": "Sanna",
        "email": "laura.sanna@holbertonschool.com",
        "avatar_url": "https://mi-bucket-imagenes.s3.us-east-1.amazonaws.com/fotos/perfil/usuario123.jpg",
        "role": "manager",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    graduated = {
        "first_name": "Federico",
        "last_name": "Paganini",
        "email": "10647@holbertonschool.com",
        "avatar_url": "https://mi-bucket-imagenes.s3.us-east-1.amazonaws.com/fotos/perfil/usuario123.jpg",
        "role": "graduated",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    response_model = graduated

    return response_model
