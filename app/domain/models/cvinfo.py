from typing import List, Optional, Literal
from datetime import datetime

from app.domain.models.bmodel import BModel


class CVInfo:
    """
    Represents a user's CV information including URLs, skills, and English proficiency.

    Attributes:
        personal_cv_url (str): URL of the personal CV.
        personal_cv_path (str): File path of the personal CV.
        linkedin_url (str): LinkedIn profile URL.
        skills (List[str]): List of skills/technologies.
        english_level (Literal["basic", "intermediate", "advanced"]): English proficiency level.
        works_in_it (bool): Whether the user works in IT.
        last_update (datetime, optional): Last time the CV info was updated. Defaults to current time.
    """

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
        """Initialize CVInfo with required URLs, skills, English level, IT status, and optional last update."""
        self.personal_cv_url = personal_cv_url
        self.personal_cv_path = personal_cv_path
        self.linkedin_url = linkedin_url
        self.skills = skills
        self.english_level = english_level
        self.works_in_it = works_in_it
        self.last_update = last_update

    # -------------------- Properties -------------------- #

    @property
    def personal_cv_url(self):
        """Return the personal CV URL."""
        return self.__personal_cv_url

    @property
    def personal_cv_path(self):
        """Return the personal CV file path."""
        return self.__personal_cv_path

    @property
    def linkedin_url(self):
        """Return the LinkedIn profile URL."""
        return self.__linkedin_url

    @property
    def skills(self):
        """Return the list of skills."""
        return self._skills

    @property
    def english_level(self):
        """Return the English proficiency level."""
        return self.__english_level

    @property
    def last_update(self):
        """Return the last update datetime."""
        return self.__last_update

    # -------------------- Setters -------------------- #

    @personal_cv_url.setter
    def personal_cv_url(self, value: str):
        """Validate and set personal CV URL."""
        self.__personal_cv_url = BModel.validate_url(value, "personal_cv_url")

    @personal_cv_path.setter
    def personal_cv_path(self, value: str):
        """Validate and set personal CV file path."""
        self.__personal_cv_path = BModel.validate_string(value, "personal_cv_path")

    @linkedin_url.setter
    def linkedin_url(self, value: str):
        """Validate and set LinkedIn URL."""
        self.__linkedin_url = BModel.validate_url(value, "linkedin_cv")

    @english_level.setter
    def english_level(self, value: Literal["basic", "intermediate", "advanced"]):
        """Validate and set English proficiency level."""
        VALID_ENGLISH_LEVELS = ["basic", "intermediate", "advanced"]
        if value not in VALID_ENGLISH_LEVELS:
            raise Exception("Invalid English Level")
        self.__english_level = value

    @skills.setter
    def skills(self, value: List[str]):
        """Validate and set skills list."""
        self._skills = self.validate_skill_list(value, "Skills")

    @last_update.setter
    def last_update(self, value: datetime):
        """Validate and set last_update; defaults to current time if None."""
        if not value:
            self.__last_update = datetime.now()
            return
        self.__last_update = BModel.validate_datetime(value, "last_update")

    # -------------------- Methods -------------------- #

    def add_skills(self, value: List[str]) -> list[str]:
        """
        Add new skills to the existing skills list, avoiding duplicates.

        Args:
            value (List[str]): List of new skills to add.

        Returns:
            List[str]: Updated sorted list of skills.
        """
        value = self.validate_skill_list(value, "New Skills")
        combined = set(self._skills) | set(value)
        self._skills = sorted(list(combined))
        return self._skills

    def to_dict(self):
        """
        Convert CVInfo instance to a dictionary representation.

        Returns:
            dict: Dictionary containing all CVInfo attributes.
        """
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
        """
        Validate that a list contains only strings (skills).

        Args:
            value (list[str]): List of skills to validate.
            field_name (str): Name of the field for error messages.

        Returns:
            list[str]: Validated list of skills.

        Raises:
            TypeError: If value is not a list.
            ValueError/TypeError: If any element in the list is not a valid string.
        """
        if not isinstance(value, list):
            raise TypeError(f"{field_name} must be a list of technologies")

        for skill in value:
            BModel.validate_string(skill, f"{skill} must be a string")

        return value
