from datetime import datetime
import re
import validators
from typing import Optional, List

from app.domain.bmodel import BModel


class User(BModel):
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        avatar_url: str,
        id: str | None = None,
        cohort: Optional[int] = None,
        github_info: Optional[str] = None,
        cv_info: Optional[str] = None,
        tutors_feedback: Optional[List[str]] = None,
        is_admin: bool = False,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        if cohort:
            self.cohort = cohort
        self.avatar_url = avatar_url
        if github_info:
            self.__github_info = BModel.validate_uuid(github_info, "github_info")
        if cv_info:
            self.__cv_info = BModel.validate_uuid(cv_info, "cv_info")
        if tutors_feedback:
            self.__tutors_feedback = [
                BModel.validate_uuid(feedback, "tutors_feedback")
                for feedback in tutors_feedback
            ]
        self.__is_admin = is_admin

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
        return self.__tutors_feedback

    @property
    def is_admin(self):
        return self.__is_admin

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
    def cohort(self, value: int):
        self.__cohort = BModel.validate_number(value, "Cohort")

    @avatar_url.setter
    def avatar_url(self, value: str):
        value = value.strip()
        if not validators.url(value):
            raise ValueError(f"avatar_url is not a valid URL")
        self.__avatar_url = value

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "is_admin": self.is_admin,
        }

        if hasattr(self, f"_User__github_info"):
            data["github_info"] = self.github_info
        if hasattr(self, "_User__cv_info"):
            data["cv_info"] = self.cv_info
        if hasattr(self, "_User__tutors_feedback"):
            data["tutors_feedback"] = self.tutors_feedback
        if hasattr(self, "_User__cohort"):
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
            f"User(id={self.id!r}, "
            f"first_name={self.first_name!r}, last_name={self.last_name!r}, "
            f"email={self.email!r}, is_admin={self.is_admin!r})"
        )
