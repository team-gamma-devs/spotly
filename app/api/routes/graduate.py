from fastapi import APIRouter, HTTPException, status, Request

from app.logger import get_logger
from app.services.use_cases.get_user import GetUser
from app.services.exceptions.user_login_exceptions import (
    UserNotLoggedIn,
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/graduate",
    tags=["graduate"],
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_data(request: Request):
    # email = request.state.user.get("email")
    email = "perfedefer@gmail.com"
    get_user = GetUser()

    try:
        user = await get_user.get_user_by_email(email)
    except UserNotLoggedIn as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return user.to_dict()
