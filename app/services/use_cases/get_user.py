from jose import jwt, JWTError

from typing import Any

from app.logger import get_logger
from app.settings import settings
from app.domain.models.user import User
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.services.exceptions.user_login_exceptions import UserNotLoggedIn

logger = get_logger(__name__)


class GetUser:
    def __init__(
        self,
        user_repo: UserRepository = None,
    ):
        self.user_repo = user_repo or UserRepository()

    async def verify(self, user: dict[str, Any]) -> dict[str, Any]:
        user_metadata = self._extract_metadata(user)
        user_data = await self._get_user_by_email(user["email"])
        return user_metadata | user_data.to_dict() if user_data else user_metadata

    def _extract_metadata(self, user: str):
        user_metadata = user["user_metadata"]
        data = {
            "email": user["email"],
            "role": user_metadata["role"],
            "is_first_time": user_metadata["is_first_time"],
        }
        return data

    async def _get_user_by_email(self, email: str) -> User:
        user = await self.user_repo.find_by_email(email)
        if not user:
            return None
        return User(**user)
