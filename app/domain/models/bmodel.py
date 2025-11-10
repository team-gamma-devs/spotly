from abc import ABC, abstractmethod
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from bson import ObjectId
from bson.errors import InvalidId
import validators
from typing import Optional


class BModel(ABC):
    """
    Base abstract model class for all entities.

    Attributes:
        id (str, optional): Unique identifier (usually MongoDB ObjectId).
        created_at (datetime): Timestamp of creation.
        updated_at (datetime): Timestamp of last update.

    Provides:
        - Basic validation utilities (string, email, number, URL, boolean, datetime, ID).
        - Abstract method `to_dict` to convert model instances to dictionaries.
    """

    def __init__(
        self,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """Initialize the model with optional id, created_at, and updated_at."""
        self.__id = id
        self.__created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    @property
    def id(self):
        """Return the unique identifier of the model."""
        return self.__id

    @property
    def created_at(self):
        """Return the creation timestamp of the model."""
        return self.__created_at

    @abstractmethod
    def to_dict(self):
        """
        Convert the model instance to a dictionary.

        Must be implemented by subclasses.
        """
        pass

    @staticmethod
    def validate_string(value: str, field_name: str) -> str:
        """
        Validate a non-empty string and remove leading/trailing whitespace.

        Args:
            value (str): The string to validate.
            field_name (str): Name of the field (used in error messages).

        Returns:
            str: The validated and stripped string.

        Raises:
            TypeError: If the value is not a string.
            ValueError: If the string is empty after stripping.
        """
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string!")
        value = value.strip()
        if len(value) == 0:
            raise ValueError(f"{field_name} cannot be empty!")
        return value

    @staticmethod
    def validate_email(value: str) -> str:
        """
        Validate the syntax of an email and return it in lowercase.

        Args:
            value (str): Email string to validate.

        Returns:
            str: Lowercased, validated email.

        Raises:
            ValueError: If the email is invalid.
        """
        value = BModel.validate_string(value, "email")
        try:
            valid = validate_email(value)
            return valid.email.lower()
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {e}")

    @staticmethod
    def validate_number(value: int, field_name: str) -> int:
        """
        Validate that a number is an integer and positive.

        Note:
            `type(value) is not int` is used intentionally to reject booleans.

        Args:
            value (int): The number to validate.
            field_name (str): Name of the field (for error messages).

        Returns:
            int: The validated number.

        Raises:
            TypeError: If value is not an integer.
            ValueError: If value is non-positive.
        """
        if type(value) is not int:
            raise TypeError(f"{field_name} must be a number")
        if value <= 0:
            raise ValueError(f"{field_name} must be positive")
        return value

    @staticmethod
    def validate_id(value: str, field_name: str) -> str:
        """
        Validate that a string is a valid MongoDB ObjectId.

        Args:
            value (str): The ID string to validate.
            field_name (str): Name of the field (for error messages).

        Returns:
            str: The validated ID string.

        Raises:
            Exception: If the ID is invalid.
        """
        try:
            ObjectId(value)
            return value
        except (InvalidId, TypeError):
            raise Exception(f"{field_name} is not a valid ID")

    @staticmethod
    def validate_url(value: str, field_name: str) -> str:
        """
        Validate that a string is a valid URL.

        Args:
            value (str): URL string to validate.
            field_name (str): Name of the field (for error messages).

        Returns:
            str: The validated URL.

        Raises:
            Exception: If the URL is invalid.
        """
        value = value.strip()
        if not validators.url(value):
            raise Exception(f"{field_name} is not a valid URL")
        return value

    @staticmethod
    def validate_bool(value: bool, field_name: str) -> bool:
        """
        Validate that a value is a boolean.

        Args:
            value (bool): Value to validate.
            field_name (str): Name of the field (for error messages).

        Returns:
            bool: The validated boolean value.

        Raises:
            Exception: If the value is not a boolean.
        """
        if not isinstance(value, bool):
            raise Exception(f"{field_name} must be a boolean")
        return value

    @staticmethod
    def validate_datetime(value: datetime, field_name: str) -> datetime:
        """
        Validate that a datetime is a valid datetime object and not in the past.

        Args:
            value (datetime): Datetime to validate.
            field_name (str): Name of the field (for error messages).

        Returns:
            datetime: The validated datetime.

        Raises:
            TypeError: If value is not a datetime object.
            ValueError: If datetime is earlier than the current time.
        """
        if not isinstance(value, datetime):
            raise TypeError(f"{field_name} must be a valid datetime")
        if value < datetime.now():
            raise ValueError(
                f"{field_name} cannot be earlier than the current date/time"
            )
        return value
