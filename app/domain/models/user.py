from datetime import datetime
import re
from typing import Optional, List, Dict, Any

from app.domain.models.bmodel import BModel
from app.domain.models.cvinfo import CVInfo


class User(BModel):
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        avatar_url: str,
        id: Optional[str] = None,
        cohort: Optional[int] = None,
        github_info: Optional[str] = None,
        cv_info: Optional[CVInfo] = None,
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
        self.__github_info = github_info
        self.cv_info = cv_info
        self._tutors_feedback = tutors_feedback
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
    def github_info(self):
        return self.__github_info

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

    @avatar_url.setter
    def avatar_url(self, value: str):
        self.__avatar_url = BModel.validate_url(value, "avatar_url")

    @cv_info.setter
    def cv_info(self, value: Optional[CVInfo]):
        if not value:
            self.__cv_info = None
        if not isinstance(value, CVInfo):
            raise Exception("cv_info must be a instantiated class of CVInfo")
        self.__cv_info = value.to_dict()

    def tutors_feedback_add(self, feedback: Dict[str, Any]):
        pass

    def to_dict(self) -> dict:
        data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        if self.id:
            data["id"] = self.id
        if self.github_info:
            data["github_info"] = self.github_info
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
