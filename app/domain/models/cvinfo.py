from typing import List, Optional, Literal
from datetime import datetime

from app.domain.models.bmodel import BModel


class CVInfo:
    def __init__(
        self,
        personal_cv_url: str,
        personal_cv_path: str,
        linkedin_url: str,
        skills: List[str],
        english_level: Literal["basic", "intermediate", "advanced"],
        works_in_it: bool,
        last_update: Optional[datetime] = None,
    ):
        self.personal_cv_url = personal_cv_url
        self.personal_cv_path = personal_cv_path
        self.linkedin_url = linkedin_url
        self.skills = skills
        self.english_level = english_level
        self.works_in_it = works_in_it
        self.last_update = last_update

    @property
    def personal_cv_url(self):
        return self.__personal_cv_url

    @property
    def personal_cv_path(self):
        return self.__personal_cv_path

    @property
    def linkedin_url(self):
        return self.__linkedin_url

    @property
    def skills(self):
        return self._skills

    @property
    def english_level(self):
        return self.__english_level

    @property
    def last_update(self):
        return self.__last_update

    @personal_cv_url.setter
    def personal_cv_url(self, value: str):
        self.__personal_cv_url = BModel.validate_url(value, "personal_cv_url")

    @personal_cv_path.setter
    def personal_cv_path(self, value: str):
        self.__personal_cv_path = BModel.validate_string(value, "personal_cv_path")

    @linkedin_url.setter
    def linkedin_url(self, value: str):
        self.__linkedin_url = BModel.validate_url(value, "linkedin_cv")

    @english_level.setter
    def english_level(self, value: Literal["basic", "intermediate", "advanced"]):
        VALID_ENGLISH_LEVELS = ["basic", "intermediate", "advanced"]
        if value not in VALID_ENGLISH_LEVELS:
            raise Exception("Invalid English Level")
        self.__english_level = value

    @skills.setter
    def skills(self, value: List[str]):
        self._skills = self.validate_skill_list(value, "Skills")

    @last_update.setter
    def last_update(self, value: datetime):
        if not value:
            self.__last_update = datetime.now()
            return

        self.__last_update = BModel.validate_datetime(value, "last_update")

    def add_skills(self, value: List[str]) -> list[str]:
        value = self.validate_skill_list(value, "New Skills")
        combined = set(self._skills) | set(value)
        self._skills = sorted(list(combined))
        return self._skills

    def to_dict(self):
        return {
            "personal_cv_url": self.personal_cv_url,
            "personal_cv_path": self.personal_cv_path,
            "linkedin_url": self.linkedin_url,
            "skills": self.skills,
            "english_level": self.english_level,
            "works_in_it": self.works_in_it,
            "last_update": self.last_update,
        }

    @staticmethod
    def validate_skill_list(value: list[str], field_name: str) -> list[str]:
        if not isinstance(value, list):
            raise TypeError(f"{field_name} mus be a list of technologies")

        for skill in value:
            BModel.validate_string(skill, f"{skill} must be a string")

        return value
