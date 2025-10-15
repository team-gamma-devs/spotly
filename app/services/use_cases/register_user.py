import logging
from datetime import datetime, timezone

from app.domain.models.invitation import Invitation
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)
from app.services.exceptions.register_user_exceptions import (
    InvitationNotFound,
    InvitationExpired,
)

logger = logging.getLogger(__name__)


class RegisterUser:
    def __init__(
        self,
        user_repo: UserRepository = None,
        invitation_repo: InvitationRepository = None,
    ):
        # self.process_cv = CVProcessor()
        self.user_repo = user_repo or UserRepository()
        self.invitation_repo = invitation_repo or InvitationRepository()

    def register_user(
        self, personal_cv, linkedin_cv, avatar_img: str, github_username: str
    ):
        pass

    async def check_invitation(self, token: str) -> bool:
        invitation_data = await self.invitation_repo.find_by_token(token)
        if not invitation_data:
            raise InvitationNotFound(
                "The token does not correspond to a valid invitation."
            )

        invitation = Invitation(**invitation_data)
        now = datetime.now()
        if invitation.expires_at < now:
            raise InvitationExpired(
                "The invitation linked to the provided token is expired"
            )
        return True if invitation.token_state == False else False
