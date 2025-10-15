from jose import jwt, JWTError

from app.settings import settings
from app.domain.models.invitation import Invitation
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)
from app.services.exceptions.user_login_exceptions import UserNotRegistered


class GetUser:
    def __init__(
        self,
        user_repo: InvitationRepository = None,
    ):
        self.user_repo = user_repo or InvitationRepository()

    async def execute(self, token: str) -> str:
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            user_id: str = payload.get("sub")

            if user_id is None:
                raise JWTError
        except JWTError:
            raise UserNotRegistered("Expired or invalid token")

        # Buscar el usuario en la BD
        user = await self.user_repo.find_by_id(user_id)

        if user is None:
            raise UserNotRegistered("User not found")

        return Invitation(**user)
