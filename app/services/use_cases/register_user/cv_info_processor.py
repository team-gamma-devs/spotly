from fastapi import UploadFile
from typing import Dict, Any

from app.domain.models.cvinfo import CVInfo
from app.infrastructure.database.repositories.cv_info_repository import (
    CVInfoRepository,
)
from app.infrastructure.database.repositories.filters_repository import (
    FiltersRepository,
)


class CVInfoProcessor:
    def __init__(
        self,
        cv_info_repo: CVInfoRepository = None,
        filters_repo: FiltersRepository = None,
        bucket_service=None,
    ):
        self.cv_info_repo = cv_info_repo or CVInfoRepository()
        self.filters_repo = filters_repo or FiltersRepository()
        self.bucket_service = bucket_service

    async def process_cv_info(
        self, cv_info: Dict[str, Any], user_id: str, cv_file: UploadFile
    ) -> str:
        cv_file_url = await self._upload_cv(cv_file)
        cv_data = {
            "graduated_id": user_id,
            "personal_cv_url": "https://placeholder.com",
            "skills": cv_info["skills"],
            "english_level": cv_info["english_level"],
            "works_in_it": cv_info["works_in_it"],
        }
        user_cv_data = CVInfo(**cv_data)
        user_cv_data_id = await self._save_cv_data(user_cv_data)
        if not user_cv_data_id:
            raise Exception("Unexpected error saving user_data in DB")

    async def _upload_cv(self, cv_file: UploadFile) -> str:
        pass

    async def _save_cv_data(self, user_cv_data: CVInfo) -> str:
        return self.cv_info_repo.create(user_cv_data.to_dict())
