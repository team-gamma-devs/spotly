from fastapi import UploadFile
from typing import Dict, Any, Optional
from PIL import Image
from io import BytesIO

from app.logger import get_logger
from app.settings import settings
from app.domain.models.user import User
from app.domain.models.cvinfo import CVInfo
from app.infrastructure.supabase import supabase_client
from app.domain.ports.supabase_storage_port import ISupabaseStorage
from app.infrastructure.supabase.bucket_service import SupabaseStorageRepository
from app.infrastructure.database.repositories.user_repository import (
    UserRepository,
)

from app.services.exceptions.register_user_exceptions import (
    InvalidFileType,
    FileTooLarge,
    UserAlreadyExists,
)

logger = get_logger(__name__)


class UserProcessor:
    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        supabase_service=None,
        bucket_service: Optional[ISupabaseStorage] = None,
    ):
        self.user_repo = user_repo or UserRepository()
        self.supabase_service = supabase_service or supabase_client
        self.bucket_service = bucket_service or SupabaseStorageRepository()

    async def process_user(
        self,
        cv_info: Dict[str, Any],
        cv_info_data: CVInfo,
        avatar_img: UploadFile,
        email: str,
        cohort: int,
        github: Optional[str],
    ):
        if await self.user_repo.user_email_exists(email):
            raise UserAlreadyExists(f"User with email {email} already registered")

        await self._validate_img(avatar_img)
        avatar_img_url = await self._save_avatar_img(avatar_img)
        user_data = {
            "first_name": cv_info["first_name"],
            "last_name": cv_info["last_name"],
            "email": email,
            "avatar_url": avatar_img_url["file_url"],
            "avatar_path": avatar_img_url["file_path"],
            "cohort": cohort,
            "cv_info": cv_info_data.to_dict(),
        }

        if github:
            user_data["github"] = f"https://github.com/{github}"

        new_user = User(**user_data)
        user_id = await self._save_user(new_user)

        self._change_user_state(email)
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

    def _change_user_state(self, email: str):
        users = supabase_client.auth.admin.list_users()
        logger.info(f"Response supabase: {users}")
        target_user = next((u for u in users if u.email == email), None)

        if not target_user:
            raise ValueError(f"User with email {email} not found")

        supabase_client.auth.admin.update_user_by_id(
            target_user.id, attributes={"user_metadata": {"is_first_time": False}}
        )
