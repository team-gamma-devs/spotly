from abc import ABC, abstractmethod
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from bson import ObjectId
from bson.errors import InvalidId
import validators
from typing import Optional


class BModel(ABC):
    def __init__(
        self,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.__id = id
        self.__created_at = self.validate_datetime(created_at) or datetime.now()
        self.updated_at = self.validate_datetime(updated_at) or datetime.now()

    @property
    def id(self):
        return self.__id

    @property
    def created_at(self):
        return self.__created_at

    @abstractmethod
    def to_dict(self):
        pass

    @staticmethod
    def validate_string(value: str, field_name: str) -> str:
        """Validate non-empty string and strip whitespace."""
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string!")
        value = value.strip()
        if len(value) == 0:
            raise ValueError(f"{field_name} cannot be empty!")
        return value

    @staticmethod
    def validate_email(value: str) -> str:
        """Validate email syntax using email_validator and return lowercased email."""
        value = BModel.validate_string(value, "email")
        try:
            valid = validate_email(value)
            return valid.email.lower()
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {e}")

    @staticmethod
    def validate_number(value: int, field_name: str) -> int:
        """
        Validate a number.

        Uses `type(value) is not int` intentionally to reject booleans.
        """
        if type(value) is not int:
            raise TypeError(f"{field_name} must be a number")
        if value <= 0:
            raise ValueError(f"{field_name} must be positive")
        return value

    @staticmethod
    def validate_id(value: str, field_name: str) -> str:
        try:
            ObjectId(value)
            return value
        except (InvalidId, TypeError):
            raise Exception(f"{field_name} is not a valid ID")

    @staticmethod
    def validate_url(value: str, field_name: str) -> str:
        value = value.strip()
        if not validators.url(value):
            raise Exception(f"{field_name} is not a valid URL")
        return value

    @staticmethod
    def validate_bool(value: bool, field_name: str) -> bool:
        if not isinstance(value, bool):
            raise Exception(f"{field_name} must be a boolean")
        return value

    @staticmethod
    def validate_datetime(value: datetime, field_name: str) -> datetime:
        if not isinstance(value, datetime):
            raise TypeError(f"{field_name} must be a valid datetime")
        if value < datetime.now():
            raise ValueError(
                f"{field_name} cannot be earlier than the current date/time"
            )
