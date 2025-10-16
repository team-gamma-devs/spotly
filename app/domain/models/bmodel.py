from abc import ABC, abstractmethod
from datetime import datetime, timezone
from email_validator import validate_email, EmailNotValidError
from uuid import uuid4, UUID


class BModel(ABC):
    def __init__(
        self,
        id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        if id:
            self.__id = id
        self.__created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

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
