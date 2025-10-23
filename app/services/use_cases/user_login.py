from datetime import datetime, timedelta
from jose import jwt
import logging
from typing import Dict, Any

from app.settings import settings
from app.domain.models.user import User
from app.domain.models.invitation import Invitation
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)
from app.services.exceptions.user_login_exceptions import (
    InvitationNotFound,
    InvitationExpired,
)

logger = logging.getLogger(__name__)


class UserLogin:
    def __init__(
        self,
        user_repo: UserRepository = None,
        invitation_repo: InvitationRepository = None,
    ):
        self.user_repo = user_repo or UserRepository()
        self.invitation_repo = invitation_repo or InvitationRepository()

    async def login(self, email: str) -> Dict[str, Any]:
        user = await self._verify_user(email)
        data = {"is_first_time": False, "role": "graduated"}
        if not user:
            invitation = await self._verify_invitation(email)
            if not invitation:
                logger.warning(f"User {email} attempted to login but is not invited")
                raise InvitationNotFound(
                    "Your email is not associated with a registered user or any invitation. Please contact the Holberton staff."
                )

            if not invitation.is_valid():
                logger.warning(
                    f"User {email} was invited but the invitation has expired"
                )
                raise InvitationExpired(
                    "The provided email corresponds to an invited user, but the invitation has expired. Please contact the Holberton staff."
                )

            data["is_first_time"] = True
        else:
            data["token"] = self._generate_jwt(user)
            data["role"] = user.role

        return data

    async def _verify_user(self, email: str) -> User:
        user_data = await self.user_repo.find_by_email(email)
        if not user_data:
            return None
        user = User(**user_data)
        return user

    async def _verify_invitation(self, email: str) -> Invitation:
        invitation_data = await self.invitation_repo.find_by_email(email)
        if not invitation_data:
            return None
        invitation = Invitation(**invitation_data)
        return invitation

    def _generate_jwt(self, user: User) -> str:
        expire = datetime.now() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        payload = {"sub": str(user.id), "exp": expire}

        token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
        return token
