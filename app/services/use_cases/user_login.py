from datetime import datetime, timedelta
from jose import jwt
import logging

from app.settings import settings
from app.domain.models.user import User
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.services.exceptions.user_login_exceptions import UserNotRegistered

logger = logging.getLogger(__name__)


class UserLogin:
    def __init__(
        self,
        user_repo: UserRepository = None,
    ):
        self.user_repo = user_repo or UserRepository()

    async def login(self, email: str) -> str:
        user = await self._verify_user(email)
        logger.info(f"User model: {user.to_dict()}")
        expire = datetime.now() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        payload = {"sub": str(user.id), "exp": expire}

        token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
        data = {"token": token, "role": user.role}
        return data

    async def _verify_user(self, email: str) -> User:
        user_data = await self.user_repo.find_by_email(email)
        if not user_data:
            raise UserNotRegistered("Invalid email")
        user = User(**user_data)
        return user
