from fastapi import UploadFile
from typing import Dict, Any, List, Optional

from app.logger import get_logger
from app.domain.models.cvinfo import CVInfo
from app.infrastructure.supabase.bucket_service import SupabaseStorageRepository
from app.domain.ports.supabase_storage_port import ISupabaseStorage
from app.infrastructure.database.repositories.filters_repository import (
    FiltersRepository,
)

logger = get_logger(__name__)


class CVInfoProcessor:
    """
    Processes CV information for a user, including file upload and filter updates.

    Attributes:
        filters_repo (FiltersRepository): Repository for managing user filters.
        bucket_service (ISupabaseStorage): Service for uploading files to Supabase storage.
    """

    def __init__(
        self,
        filters_repo: Optional[FiltersRepository] = None,
        bucket_service: Optional[ISupabaseStorage] = None,
    ):
        """
        Initialize the CVInfoProcessor with optional repository and storage service.

        Args:
            filters_repo (FiltersRepository | None): Repository instance for filters.
                Defaults to a new FiltersRepository.
            bucket_service (ISupabaseStorage | None): Storage service for file uploads.
                Defaults to a new SupabaseStorageRepository.
        """
        self.filters_repo = filters_repo or FiltersRepository()
        self.bucket_service = bucket_service or SupabaseStorageRepository()

    async def process_cv_info(
        self, cv_info: Dict[str, Any], cv_file: UploadFile
    ) -> CVInfo:
        """
        Process user CV information: upload CV file, create CVInfo object, and update filters.

        Args:
            cv_info (dict): Dictionary containing CV details, must include:
                - "linkedin_url" (str)
                - "skills" (List[str])
                - "english_level" (Literal["basic","intermediate","advanced"])
                - "works_in_it" (bool)
            cv_file (UploadFile): PDF file of the user's CV.

        Returns:
            CVInfo: Processed CVInfo object containing validated data and uploaded file info.
        """
        cv_file_data = await self._upload_cv(cv_file)
        cv_data = {
            "personal_cv_url": cv_file_data["file_url"],
            "personal_cv_path": cv_file_data["file_path"],
            "linkedin_url": cv_info["linkedin_url"],
            "skills": cv_info["skills"],
            "english_level": cv_info["english_level"],
            "works_in_it": cv_info["works_in_it"],
        }
        logger.info(f"CV data to check: {cv_data}")
        user_cv_data = CVInfo(**cv_data)
        logger.info(f"CV data to save: {user_cv_data.to_dict()}")

        await self._update_filters(user_cv_data.skills)
        return user_cv_data

    async def _upload_cv(self, cv_file: UploadFile) -> Dict[str, str]:
        """
        Upload the CV file to Supabase storage.

        Args:
            cv_file (UploadFile): File to upload.

        Returns:
            dict: Dictionary containing:
                - "file_url": Public URL of the uploaded file.
                - "file_path": Internal storage path of the file.
        """
        return await self.bucket_service.upload(cv_file, "cvs_pdf")

    async def _update_filters(self, filters: List[str]):
        """
        Add user skills to the filters repository.

        Args:
            filters (List[str]): List of skill strings to add to filters.
        """
        await self.filters_repo.add_user_filters(filters)
        logger.info(f"Filters correctly added to list")
