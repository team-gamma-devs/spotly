from jose import jwt, JWTError
import logging

from app.settings import settings
from app.domain.models.user import User
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.services.exceptions.user_login_exceptions import UserNotRegistered

logger = logging.getLogger(__name__)


class GetUser:
    def __init__(
        self,
        user_repo: UserRepository = None,
    ):
        self.user_repo = user_repo or UserRepository()

    async def verify(self, token: str) -> User:
        try:
            logger.info(f"Token: {token}")
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            user_id: str = payload.get("sub")
            logger.info(f"Payload: {payload}, User_id: {user_id}, Token: {token}")

            if user_id is None:
                raise JWTError
        except JWTError as e:
            logging.warning(f"Error: {e}")
            raise UserNotRegistered("Expired or invalid token")

        user = await self.user_repo.find_by_id(user_id)

        if user is None:
            raise UserNotRegistered("User not found")

        return User(**user)
