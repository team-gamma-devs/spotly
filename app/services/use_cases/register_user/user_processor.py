from fastapi import UploadFile
from typing import Dict, Any, Optional
from PIL import Image
from io import BytesIO
import logging

from app.settings import settings
from app.domain.models.user import User
from app.domain.models.cvinfo import CVInfo
from app.domain.ports.supabase_storage_port import ISupabaseStorage
from app.infrastructure.database.repositories.user_repository import (
    UserRepository,
)

from app.services.exceptions.register_user_exceptions import (
    InvalidFileType,
    FileTooLarge,
)

logger = logging.getLogger(__name__)


class UserProcessor:
    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        bucket_service: Optional[ISupabaseStorage] = None,
    ):
        self.user_repo = user_repo or UserRepository()
        self.bucket_service = bucket_service

    async def process_user(
        self,
        cv_info: Dict[str, Any],
        cv_info_data: CVInfo,
        avatar_img: UploadFile,
        email: str,
        cohort: int,
        github: str,
    ):
        if await self.user_repo.user_email_exists(email):
            raise Exception(f"User with email {email} already registered")

        await self._validate_img(avatar_img)
        avatar_img_url = await self._save_avatar_img(avatar_img)
        user_data = {
            "first_name": cv_info["first_name"],
            "last_name": cv_info["last_name"],
            "email": email,
            "avatar_url": avatar_img_url["file_url"],
            "avatar_path": avatar_img_url["file_path"],
            "cohort": cohort,
            "cv_info": cv_info_data,
        }

        if github:
            user_data["github"] = github

        new_user = User(**user_data)
        user_id = await self._save_user(new_user)
        return user_id

    async def _save_avatar_img(self, avatar_img: UploadFile) -> dict[str, str]:
        return await self.bucket_service.upload(avatar_img, "avatars")

    async def _save_user(self, new_user: User) -> str:
        user_id = await self.user_repo.create(new_user.to_dict())
        return user_id

    async def _validate_img(self, file: UploadFile):
        MAX_IMG_SIZE_BYTES = settings.max_img_size * 1024 * 1024

        if not file.content_type.startswith("image/"):
            raise InvalidFileType(f"{file.filename} is not a valid image")

        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        if size > MAX_IMG_SIZE_BYTES:
            raise FileTooLarge(
                f"{file.filename} exceeds {settings.max_img_size:.1f}MB limit"
            )

        try:
            img = Image.open(BytesIO(await file.read()))
            img.verify()
        except Exception:
            raise InvalidFileType(f"{file.filename} is not a valid image")
        finally:
            await file.seek(0)
