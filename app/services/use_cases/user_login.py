import logging

from app.settings import settings
from app.domain.models.user import User
from app.domain.models.invitation import Invitation
from app.infrastructure.supabase import supabase_client
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
    """
    Service responsible for handling user login via Supabase magic links.

    Verifies if a user exists or checks invitations for non-registered users,
    then triggers sending a magic link to the provided email.
    """

    def __init__(
        self,
        login_client=supabase_client,
        user_repo: UserRepository = None,
        invitation_repo: InvitationRepository = None,
    ):
        """
        Initialize the UserLogin service.

        Args:
            login_client: Supabase client instance used for authentication.
            user_repo (UserRepository, optional): Repository to manage user data.
            invitation_repo (InvitationRepository, optional): Repository to manage invitation data.
        """
        self.login_client = login_client
        self.user_repo = user_repo or UserRepository()
        self.invitation_repo = invitation_repo or InvitationRepository()

    async def login(self, email: str):
        """
        Attempt to log in a user with the provided email.

        If the user exists, a magic link is sent directly.
        If the user does not exist, verifies if there is a valid invitation first.

        Args:
            email (str): The email of the user attempting to log in.

        Raises:
            InvitationNotFound: If no invitation exists for a non-registered email.
            InvitationExpired: If the invitation for a non-registered email has expired.
        """
        user = await self._verify_user(email)
        logger.info(f"user: {user}")
        if not user:
            await self._verify_invitation(email)

        magic_link = {
            "email": email,
            "options": {
                "should_create_user": False,
                "email_redirect_to": settings.supabase_redirect_url,
            },
        }
        self.login_client.auth.sign_in_with_otp(magic_link)
        logger.info(f"Magic Link correctly sent to {email}")

    async def _verify_user(self, email: str) -> User:
        """
        Check if a user with the given email exists in the database.

        Args:
            email (str): Email to search for.

        Returns:
            User | None: Returns a User object if found, otherwise None.
        """
        user_data = await self.user_repo.find_by_email(email)
        if not user_data:
            return None
        user = User(**user_data)
        return user

    async def _verify_invitation(self, email: str):
        """
        Check if a valid invitation exists for the given email.

        Args:
            email (str): Email to check for invitation.

        Raises:
            InvitationNotFound: If no invitation exists for the email.
            InvitationExpired: If the invitation exists but has expired.
        """
        invitation_data = await self.invitation_repo.find_by_email(email)
        if not invitation_data:
            logger.warning(f"User {email} attempted to login but is not invited")
            raise InvitationNotFound(
                "Your email is not associated with a registered user or any invitation. Please contact the Holberton staff."
            )

        logger.info(f"invitation_data: {invitation_data}")
        invitation = Invitation(**invitation_data)
        if not invitation.is_valid():
            logger.warning(f"User {email} was invited but the invitation has expired")
            raise InvitationExpired(
                "The provided email corresponds to an invited user, but the invitation has expired. Please contact the Holberton staff."
            )
