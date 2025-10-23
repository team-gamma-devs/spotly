from fastapi import UploadFile
from typing import Dict, Any, List, Optional
import logging

from app.domain.models.cvinfo import CVInfo
from app.infrastructure.database.repositories.filters_repository import (
    FiltersRepository,
)

logger = logging.getLogger(__name__)


class CVInfoProcessor:
    def __init__(
        self,
        filters_repo: Optional[FiltersRepository] = None,
        bucket_service=None,
    ):
        self.filters_repo = filters_repo or FiltersRepository()
        self.bucket_service = bucket_service

    async def process_cv_info(
        self, cv_info: Dict[str, Any], cv_file: UploadFile
    ) -> CVInfo:
        cv_file_url = await self._upload_cv(cv_file)
        cv_data = {
            "personal_cv_url": cv_file_url,
            "skills": cv_info["skills"],
            "english_level": cv_info["english_level"],
            "works_in_it": cv_info["works_in_it"],
        }

        user_cv_data = CVInfo(**cv_data)
        logger.info(f"CV data to save: {user_cv_data.to_dict()}")

        await self._update_filters(user_cv_data.skills)
        return user_cv_data

    async def _upload_cv(self, cv_file: UploadFile) -> str:
        return "https://placeholder.com"

    async def _update_filters(self, filters: List[str]):
        await self.filters_repo.add_user_filters(filters)
        logger.warning(f"Filters correctly added to list")
