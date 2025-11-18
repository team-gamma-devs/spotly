from typing import Any, Optional

from app.logger import get_logger
from app.settings import settings
from app.domain.models.user import User
from app.infrastructure.database.repositories.user_repository import (
    UserRepository,
)
from app.services.exceptions.user_login_exceptions import UserNotLoggedIn

logger = get_logger(__name__)


class GetUser:
    """
    Use case for retrieving and verifying a user.

    Attributes:
        user_repo (UserRepository): Repository to access user data.
    """

    def __init__(self, user_repo: Optional[UserRepository] = None):
        """
        Initialize the GetUser use case.

        Args:
            user_repo (UserRepository, optional): Custom user repository.
                Defaults to standard UserRepository.
        """
        self.user_repo = user_repo or UserRepository()

    async def verify(self, user: dict[str, Any]) -> dict[str, Any]:
        """
        Verify a user and return combined metadata and database information.

        Args:
            user (dict[str, Any]): Dictionary representing the user from authentication system.

        Returns:
            dict[str, Any]: Combined dictionary of user metadata and database information.
                If user is not found in the database, returns only the metadata.
        """
        user_metadata = self._extract_metadata(user)
        user_data = await self._get_user_by_email(user["email"])
        return user_metadata | user_data.to_dict() if user_data else user_metadata

    def _extract_metadata(self, user: dict[str, Any]) -> dict[str, Any]:
        """
        Extract relevant metadata from the authentication user dictionary.

        Args:
            user (dict[str, Any]): User dictionary from authentication system.

        Returns:
            dict[str, Any]: Dictionary containing 'email', 'role', and 'is_first_time'.
        """
        user_metadata = user["user_metadata"]
        data = {
            "email": user["email"],
            "role": user_metadata["role"],
            "is_first_time": user_metadata["is_first_time"],
        }
        return data

    async def _get_user_by_email(self, email: str) -> User | None:
        """
        Fetch a user from the database by email.

        Args:
            email (str): User's email address.

        Returns:
            User | None: User instance if found, None otherwise.
        """
        user = await self.user_repo.find_by_email(email)
        if not user:
            return None

        if "_id" in user:
            user["id"] = str(user.pop("_id"))

        user_fields = {
            "id": user.get("id"),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "email": user.get("email"),
            "avatar_url": user.get("avatar_url"),
            "avatar_path": user.get("avatar_path"),
            "cohort": user.get("cohort"),
            "github_url": user.get("github_url"),
            "cv_info": user.get("cv_info"),
            "tutors_feedback": user.get("tutors_feedback"),
            "role": user.get("role", "graduate"),
            "created_at": user.get("created_at"),
            "updated_at": user.get("updated_at"),
        }

        return User(**user_fields)
