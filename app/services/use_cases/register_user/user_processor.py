from fastapi import UploadFile
from typing import Dict, Any, Optional
import logging

from app.domain.models.user import User
from app.domain.models.cvinfo import CVInfo
from app.infrastructure.database.repositories.user_repository import (
    UserRepository,
)

logger = logging.getLogger(__name__)


class UserProcessor:
    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        bucket_service=None,
    ):
        self.user_repo = user_repo or UserRepository()
        self.bucket_service = bucket_service

    async def process_user(
        self,
        cv_info: Dict[str, Any],
        cv_info_data: CVInfo,
        avatar_img: UploadFile,
        email: str = "perfedefer@gmail.com",
        cohort: int = 26,
    ):
        if await self.user_repo.user_email_exists(email):
            raise Exception(f"User with email {email} already registered")

        avatar_img_url = await self._save_avatar_img(avatar_img)
        user_data = {
            "first_name": cv_info["first_name"],
            "last_name": cv_info["last_name"],
            "email": email,
            "avatar_url": avatar_img_url,
            "cohort": cohort,
            "cv_info": cv_info_data,
        }

        new_user = User(**user_data)
        user_id = await self._save_user(new_user)
        return user_id

    async def _save_avatar_img(self, avatar_img: UploadFile) -> str:
        return "https://via.placeholder.com/150"

    async def _save_user(self, new_user: User) -> str:
        user_id = await self.user_repo.create(new_user.to_dict())
        return user_id

    async def update_user_external_data(
        self, user_id: str, github_info_id: Optional[str] = None
    ) -> bool:
        data = {}
        if github_info_id:
            data["github_info"] = github_info_id
        update_result = await self.user_repo.update(user_id, data)
        return update_result
