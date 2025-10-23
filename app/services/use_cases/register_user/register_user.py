from fastapi import UploadFile
import logging
from typing import Optional

from app.services.use_cases.register_user.cv_processor import CVProcessor
from app.services.use_cases.register_user.cv_info_processor import (
    CVInfoProcessor,
)
from app.services.use_cases.register_user.user_processor import UserProcessor
from app.infrastructure.database.repositories.user_repository import (
    UserRepository,
)
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)

logger = logging.getLogger(__name__)


class RegisterUser:
    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        invitation_repo: Optional[InvitationRepository] = None,
        cv_processor: Optional[CVProcessor] = None,
        cv_info_processor: Optional[CVInfoProcessor] = None,
        user_processor: Optional[UserProcessor] = None,
    ):
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
        token: Optional[str] = None,
    ):
        logger.info(f"User registration process started with token: {token}")

        cv_info = await self.cv_processor.process_cvs(personal_cv, linkedin_cv)
        logger.info(f"User cv info successfully parsed: {cv_info}")

        cv_info_data = await self.cv_info_processor.process_cv_info(
            cv_info, personal_cv
        )

        registered_user_id = await self.user_processor.process_user(
            cv_info, cv_info_data, avatar_img
        )
        logger.info(f"User registered succesfully (id): {registered_user_id}")

        if github_username:
            pass

        update_user = await self.user_processor.update_user_external_data(
            user_id=registered_user_id,
            github_info_id="",
        )

        if not update_user:
            raise Exception("Unexpected error updating user")

        return registered_user_id
