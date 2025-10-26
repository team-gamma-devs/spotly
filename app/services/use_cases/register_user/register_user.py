from fastapi import UploadFile
from typing import Optional

from app.logger import get_logger
from app.domain.models.invitation import Invitation
from app.services.use_cases.register_user.cv_processor import CVProcessor
from app.services.use_cases.register_user.cv_info_processor import CVInfoProcessor
from app.services.use_cases.register_user.user_processor import UserProcessor
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)
from app.services.exceptions.register_user_exceptions import UserAlreadyExists
from app.services.exceptions.user_login_exceptions import (
    InvitationNotFound,
    InvitationExpired,
)

logger = get_logger(__name__)


class RegisterUser:
    """
    Use case class responsible for registering a new user in the system.

    This class handles:
        - Email verification and invitation validation
        - CV processing and extraction of structured data
        - User data processing and saving to the database

    Attributes:
        user_repo (UserRepository): Repository for user data.
        invitation_repo (InvitationRepository): Repository for invitations.
        cv_processor (CVProcessor): Service for processing personal and LinkedIn CVs.
        cv_info_processor (CVInfoProcessor): Service for processing CV info into structured format.
        user_processor (UserProcessor): Service for creating and saving user records.
    """

    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        invitation_repo: Optional[InvitationRepository] = None,
        cv_processor: Optional[CVProcessor] = None,
        cv_info_processor: Optional[CVInfoProcessor] = None,
        user_processor: Optional[UserProcessor] = None,
    ):
        """
        Initialize the RegisterUser use case with optional custom repositories and services.

        Args:
            user_repo (Optional[UserRepository]): Custom user repository instance.
            invitation_repo (Optional[InvitationRepository]): Custom invitation repository instance.
            cv_processor (Optional[CVProcessor]): Custom CV processing service.
            cv_info_processor (Optional[CVInfoProcessor]): Custom CV info processing service.
            user_processor (Optional[UserProcessor]): Custom user creation service.
        """
        self.user_repo = user_repo or UserRepository()
        self.invitation_repo = invitation_repo or InvitationRepository()
        self.cv_processor = cv_processor or CVProcessor()
        self.cv_info_processor = cv_info_processor or CVInfoProcessor()
        self.user_processor = user_processor or UserProcessor()

    async def register_user(
        self,
        personal_cv: UploadFile,
        linkedin_cv: UploadFile,
        avatar_img: UploadFile,
        github_username: Optional[str] = None,
        email: Optional[str] = None,
    ):
        """
        Register a new user by processing CVs, verifying the invitation, and creating the user.

        Args:
            personal_cv (UploadFile): Personal CV PDF file uploaded by the user.
            linkedin_cv (UploadFile): LinkedIn CV PDF file uploaded by the user.
            avatar_img (UploadFile): User's avatar image file.
            github_username (Optional[str]): GitHub username of the user.
            email (Optional[str]): Email of the invited user.

        Returns:
            str: The ID of the newly registered user.

        Raises:
            UserAlreadyExists: If a user with the given email is already registered.
            InvitationNotFound: If there is no invitation for the provided email.
            InvitationExpired: If the invitation has expired.
        """
        invitation = await self._verify_email(email)
        logger.info(f"User registration process started with email: {email}")

        cv_info = await self.cv_processor.process_cvs(personal_cv, linkedin_cv)
        logger.info(f"User CV info successfully parsed: {cv_info}")

        cv_info_data = await self.cv_info_processor.process_cv_info(
            cv_info, personal_cv
        )

        registered_user_id = await self.user_processor.process_user(
            cv_info,
            cv_info_data,
            avatar_img,
            email=invitation.email,
            cohort=invitation.cohort,
            github=github_username,
        )
        logger.info(f"User registered successfully (id): {registered_user_id}")

        return registered_user_id

    async def _verify_email(self, email: str) -> Invitation:
        """
        Verify that the provided email is invited and not already registered.

        Args:
            email (str): Email address to verify.

        Returns:
            Invitation: Invitation object corresponding to the email.

        Raises:
            UserAlreadyExists: If a user with the email is already registered.
            InvitationNotFound: If no invitation exists for the email.
            InvitationExpired: If the invitation has expired.
        """
        user = await self.user_repo.find_by_email(email)
        if user:
            raise UserAlreadyExists(f"Email {email} already registered")

        invitation = await self.invitation_repo.find_by_email(email)
        if not invitation:
            raise InvitationNotFound(f"{email} is not invited, contact Holberton Staff")

        invitation = Invitation(**invitation)

        if not invitation.is_valid():
            raise InvitationExpired(
                f"{email} invitation expired. Contact Holberton Staff"
            )

        return invitation
