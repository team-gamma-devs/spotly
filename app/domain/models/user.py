from datetime import datetime
import re
from typing import Optional, List, Dict, Any

from app.domain.models.bmodel import BModel


class User(BModel):
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        avatar_url: str,
        avatar_path: str,
        id: Optional[str] = None,
        cohort: Optional[int] = None,
        github: Optional[str] = None,
        cv_info: Optional[dict] = None,
        tutors_feedback: Optional[List[str]] = None,
        role: str = "graduate",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.cohort = cohort
        self.avatar_url = avatar_url
        self.avatar_path = avatar_path
        self.github = github
        self.cv_info = cv_info
        self.tutors_feedback = tutors_feedback
        self.__role = role

    @property
    def first_name(self):
        return self.__first_name

    @property
    def last_name(self):
        return self.__last_name

    @property
    def email(self):
        return self.__email

    @property
    def cohort(self):
        return self.__cohort

    @property
    def avatar_url(self):
        return self.__avatar_url

    @property
    def avatar_path(self):
        return self.__avatar_path

    @property
    def github(self):
        return self.__github

    @property
    def cv_info(self):
        return self.__cv_info

    @property
    def tutors_feedback(self):
        return self._tutors_feedback

    @property
    def role(self):
        return self.__role

    @first_name.setter
    def first_name(self, value: str):
        self.__first_name = self.validate_alpha(value, "first_name")

    @last_name.setter
    def last_name(self, value: str):
        self.__last_name = self.validate_alpha(value, "last_name")

    @email.setter
    def email(self, value: str):
        self.__email = BModel.validate_email(value)

    @cohort.setter
    def cohort(self, value: Optional[int]):
        if not value:
            self.__cohort = None
        self.__cohort = BModel.validate_number(value, "Cohort")

    @github.setter
    def github(self, value: Optional[str]):
        if not value:
            self.__github = None

        self.__github = BModel.validate_string(value, "github")

    @avatar_url.setter
    def avatar_url(self, value: str):
        self.__avatar_url = BModel.validate_url(value, "avatar_url")

    @avatar_path.setter
    def avatar_path(self, value: str):
        self.__avatar_path = BModel.validate_string(value, "avatar_path")

    @cv_info.setter
    def cv_info(self, value: Optional[dict]):
        if not value:
            self.__cv_info = None
        if not isinstance(value, dict):
            raise Exception("cv_info must be a dict")
        self.__cv_info = value

    @tutors_feedback.setter
    def tutors_feedback(self, value: Optional[list[dict[str, Any]]]):
        if not value:
            self._tutors_feedback = None
            return

        if not isinstance(value, list):
            raise ValueError(f"{value} must be a list of feedbacks")

        self._tutors_feedback = value

    def tutors_feedback_add(self, feedback: Dict[str, Any]):
        pass

    def to_dict(self) -> dict:
        data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "avatar_path": self.avatar_path,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        if self.id:
            data["id"] = self.id
        if self.github:
            data["github"] = self.github
        if self.cv_info:
            data["cv_info"] = self.cv_info
        if self.tutors_feedback:
            data["tutors_feedback"] = self.tutors_feedback
        if self.cohort:
            data["cohort"] = self.cohort

        return data

    @staticmethod
    def validate_alpha(value: str, field_name: str) -> str:
        value = BModel.validate_string(value, field_name)
        pattern = re.compile(
            r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+(?:[-'][A-Za-zÁÉÍÓÚáéíóúÑñÜü]+)?$"
        )
        if not pattern.match(value):
            raise ValueError(
                f"{field_name} must contain only letters, and may include one hyphen or apostrophe."
            )

        return value

    def __repr__(self):
        return (
            f"first_name={self.first_name!r}, last_name={self.last_name!r}, "
            f"email={self.email!r}, role={self.role!r})"
        )
