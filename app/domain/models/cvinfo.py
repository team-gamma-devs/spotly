from typing import List
from datetime import datetime

from app.domain.models.bmodel import BModel


class CVInfo(BModel):
    def __init__(
        self,
        graduated_id: str,
        personal_cv_url: str,
        skills: List[str],
        english_level: str,
        works_in_it: bool,
        created_at: datetime,
        updated_at: datetime,
        id: str | None = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.__graduated_id = BModel.validate_id(graduated_id, "graduated_id")
        self.personal_cv_url = BModel.validate_url(personal_cv_url, "personal_cv_url")
        self.skills = skills
        self.english_level = english_level
        self.works_in_it = works_in_it

    @property
    def graduated_id(self):
        return self.__graduated_id

    @property
    def personal_cv_url(self):
        return self.__personal_cv_url

    @property
    def skills(self):
        return self.__skills

    @property
    def english_level(self):
        return self.__english_level
