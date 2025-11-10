from fastapi import UploadFile
from typing import Dict, Any, Optional
from PIL import Image
from io import BytesIO

from app.logger import get_logger
from app.settings import settings
from app.domain.models.user import User
from app.domain.models.cvinfo import CVInfo
from app.domain.models.invitation import Invitation
from app.infrastructure.supabase import supabase_client
from app.domain.ports.supabase_storage_port import ISupabaseStorage
from app.infrastructure.supabase.bucket_service import (
    SupabaseStorageRepository,
)
from app.infrastructure.database.repositories.user_repository import (
    UserRepository,
)
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)
from app.services.exceptions.register_user_exceptions import (
    InvalidFileType,
    FileTooLarge,
    UserAlreadyExists,
)

logger = get_logger(__name__)


class UserProcessor:
    """
    Service class responsible for processing and creating a new user.

    This class handles:
        - Validation and storage of avatar images
        - Creation of User objects
        - Saving users to the database
        - Updating user state in Supabase

    Attributes:
        user_repo (UserRepository): Repository for user data.
        supabase_service: Supabase client for storage and authentication.
        bucket_service (ISupabaseStorage): Service to upload files to Supabase storage.
    """

    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        invitation_repo: Optional[InvitationRepository] = None,
        supabase_service=None,
        bucket_service: Optional[ISupabaseStorage] = None,
    ):
        """
        Initialize the UserProcessor with optional custom repositories and services.

        Args:
            user_repo (Optional[UserRepository]): Custom user repository instance.
            supabase_service: Optional Supabase client instance.
            bucket_service (Optional[ISupabaseStorage]): Optional bucket service instance.
        """
        self.user_repo = user_repo or UserRepository()
        self.invitation_repo = invitation_repo or InvitationRepository()
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
    ) -> str:
        """
        Process a new user: validate avatar, save image, create user object, and save to database.

        Args:
            cv_info (Dict[str, Any]): Parsed CV data as dictionary.
            cv_info_data (CVInfo): Structured CV information object.
            avatar_img (UploadFile): User's avatar image file.
            email (str): Email of the user.
            cohort (int): Cohort number for the user.
            github (Optional[str]): GitHub username (optional).

        Returns:
            str: The ID of the newly created user.

        Raises:
            UserAlreadyExists: If a user with the given email already exists.
            InvalidFileType: If the avatar image is not valid.
            FileTooLarge: If the avatar image exceeds size limits.
        """
        if await self.user_repo.user_email_exists(email):
            raise UserAlreadyExists(
                f"User with email {email} already registered"
            )

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
        await self._change_invitation_state(email)
        return user_id

    async def _save_avatar_img(self, avatar_img: UploadFile) -> dict[str, str]:
        """
        Upload the user's avatar image to Supabase storage.

        Args:
            avatar_img (UploadFile): Avatar image file to upload.

        Returns:
            dict[str, str]: Dictionary containing the file URL and path.
        """
        return await self.bucket_service.upload(avatar_img, "avatars")

    async def _save_user(self, new_user: User) -> str:
        """
        Save the User object to the database.

        Args:
            new_user (User): User instance to save.

        Returns:
            str: ID of the newly created user.
        """
        user_id = await self.user_repo.create(new_user.to_dict())
        return user_id

    async def _validate_img(self, file: UploadFile):
        """
        Validate the uploaded image for type, size, and content integrity.

        Args:
            file (UploadFile): Image file to validate.

        Raises:
            InvalidFileType: If the file is not a valid image.
            FileTooLarge: If the image exceeds the maximum allowed size.
        """
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
        """
        Update the user state in Supabase to indicate that it is no longer the first login.

        Args:
            email (str): Email of the user to update.

        Raises:
            ValueError: If no user with the given email is found in Supabase.
        """
        users = supabase_client.auth.admin.list_users()
        logger.info(f"Response supabase: {users}")
        target_user = next((u for u in users if u.email == email), None)

        if not target_user:
            raise ValueError(f"User with email {email} not found")

        supabase_client.auth.admin.update_user_by_id(
            target_user.id,
            attributes={"user_metadata": {"is_first_time": False}},
        )

    async def _change_invitation_state(self, email: str):
        invitation = await self.invitation_repo.find_by_email(email)
        await self.invitation_repo.update(
            id_=invitation["id"], updates={"log_state": True}
        )
