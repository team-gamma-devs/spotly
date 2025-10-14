from datetime import datetime, timedelta
from jose import jwt

from app.settings import settings
from app.domain.invitation import Invitation
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)
from app.services.user_login.exceptions import UserNotRegistered


class AuthUser:
    def __init__(
        self,
        user_repo: InvitationRepository = None,
    ):
        self.user_repo = user_repo or InvitationRepository()

    async def execute(self, email: str) -> str:
        user = await self._verify_user(email)
        expire = datetime.now() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        payload = {"sub": str(user.id), "exp": expire}

        token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
        return token

    async def _verify_user(self, email: str) -> Invitation:
        user_data = await self.user_repo.find_by_email(email)
        if not user_data:
            raise UserNotRegistered("Invalid email")
        user = Invitation(**user_data)
        return user
