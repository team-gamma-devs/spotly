from fastapi import UploadFile
import logging

from app.domain.models.invitation import Invitation
from app.services.use_cases.register_user.cv_processor import CVProcessor
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)

logger = logging.getLogger(__name__)


class RegisterUser:
    def __init__(
        self,
        user_repo: UserRepository = None,
        invitation_repo: InvitationRepository = None,
        cv_processor: CVProcessor = None,
    ):
        self.cv_processor = cv_processor or CVProcessor()
        self.user_repo = user_repo or UserRepository()
        self.invitation_repo = invitation_repo or InvitationRepository()

    def register_user(
        self,
        personal_cv: UploadFile,
        linkedin_cv: UploadFile,
        avatar_img: str = None,
        github_username: str = None,
    ):
        cv_info = self.cv_processor.process_cvs(personal_cv, linkedin_cv)

        return cv_info
