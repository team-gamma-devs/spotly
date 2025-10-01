from uuid import uuid4
import secrets
import re
from datetime import datetime, timezone, timedelta
from email_validator import validate_email, EmailNotValidError


class Invitation:
    """
    Represents an invitation for a user to join a cohort.

    Attributes:
        id (str): Unique identifier for the invitation (UUID4).
        full_name (str): Full name of the invited user (readonly).
        email (str): Email of the invited user (readonly, validated for syntax).
        cohort (int): Cohort number (readonly).
        token (str): Secure URL-safe one-time token for the invitation (readonly).
        token_state (bool): Indicates if the token has been used/activated.
        log_state (bool): Indicates if the user coud registrate correctly in the app.
        created_at (datetime): UTC timestamp when the invitation was created (readonly).
        expires_at (datetime): UTC timestamp when the invitation expires (readonly).

    Behavior:
        - Token is generated automatically upon creation.
        - `token_state` and `log_state` can be modified using setters, with type validation.
        - Other attributes are immutable after instantiation.
    """

    def __init__(
        self,
        full_name: str,
        email: str,
        cohort: int,
        token: str | None = None,
        token_state: bool = False,
        log_state: bool = False,
        created_at: datetime | None = None,
        expires_at: datetime | None = None,
    ):
        """
        Initialize a new Invitation instance.

        Args:
            full_name (str): Full name of the invited user.
            email (str): Email address of the invited user.
            cohort (int): Cohort number.
            token (str): Not used; token is generated automatically.

        Raises:
            TypeError, ValueError: If any input is invalid.
        """
        self.id = str(uuid4())
        self.__full_name = self.validate_string(full_name, "full_name")
        self.__email = self.validate_email(email)
        self.__cohort = self.validate_cohort(cohort)
        self.token = token  # Generate a secure, URL-safe one-time token for the invitation
        self.token_state = token_state
        self.log_state = log_state
        self.created_at = created_at
        self.expires_at = expires_at

    @property
    def full_name(self):
        return self.__full_name

    @property
    def email(self):
        return self.__email

    @property
    def cohort(self):
        return self.__cohort

    @property
    def token(self):
        return self.__token

    @property
    def token_state(self):
        return self.__token_state

    @property
    def log_state(self):
        return self.__log_state

    @property
    def created_at(self):
        return self.__created_at

    @property
    def expires_at(self):
        return self.__expires_at

    @token.setter
    def token(self, value: str | None):
        if not value:
            self.__token = secrets.token_urlsafe(32)
            return

        value = Invitation.validate_string(value, "Token")

        if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
            raise ValueError("Token contains invalid characters!")

        if not (40 <= len(value) <= 50):
            raise ValueError(
                f"Token length must be between 40 and 50, got {len(value)}"
            )

        self.__token = value

    # Setter for state change when token is used.
    @token_state.setter
    def token_state(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("Token state must be a boolean")
        self.__token_state = value

    # Setter for log if the user coud registrate.
    @log_state.setter
    def log_state(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("Log state must be a boolean")
        self.__log_state = value

    @created_at.setter
    def created_at(self, value: datetime | None):
        if not value:
            self.__created_at = datetime.now(timezone.utc)
            return

        value = self.validate_date(value, "Created date")
        if value > datetime.now(timezone.utc):
            raise ValueError("The creation date cannot exceed current date")
        self.__created_at = value

    @expires_at.setter
    def expires_at(self, value: datetime | None):
        if not value:
            self.__expires_at = datetime.now(timezone.utc) + timedelta(days=30)
            return

        self.__expires_at = self.validate_date(value, "Expiration date")

    @staticmethod
    def validate_string(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string!")
        value = value.strip()
        if len(value) == 0:
            raise ValueError(f"{field_name} cannot be empty!")
        return value

    @staticmethod
    def validate_email(value: str) -> str:
        value = Invitation.validate_string(value, "email")
        try:
            valid = validate_email(value)
            return valid.email.lower()
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {e}")

    @staticmethod
    def validate_cohort(value: int) -> int:
        if type(value) is not int:
            raise TypeError("Cohort must be a number")
        if value <= 0:
            raise ValueError("Cohort must be positive")
        return value

    @staticmethod
    def validate_bool(value: bool, field_name: str) -> bool:
        if not isinstance(value, bool):
            raise TypeError(f"{field_name} must be a boolean")
        return value

    @staticmethod
    def validate_date(value: datetime, field_name: str) -> datetime:
        if not isinstance(value, datetime):
            raise TypeError(f"{field_name} must ve a valid date")
        return value
