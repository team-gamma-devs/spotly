import secrets
from datetime import datetime, timezone, timedelta
from app.domain.models.bmodel import BModel


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
        log_state (bool): Indicates if the user could registrate correctly in the app.
        created_at (datetime): UTC timestamp when the invitation was created (readonly).
        expires_at (datetime): UTC timestamp when the invitation expires.
    """

    def __init__(
        self,
        full_name: str,
        email: str,
        cohort: int,
        id: str | None = None,
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
            id (str|None): id (if coming from DB).
            token (str|None): Ivitation Token; generated if not provided.
            token_state (bool): Whether the token was used.
            log_state (bool): Whether registration was completed.
            created_at (datetime|None): Creation timestamp (UTC). Defaults to now UTC.
            expires_at (datetime|None): Expiration timestamp (UTC). Defaults to created_at + 30 days.

        Raises:
            TypeError, ValueError: If any input is invalid.
        """
        if id:
            self.__id = id
        self.__full_name = BModel.validate_string(full_name, "full_name")
        self.__email = BModel.validate_email(email)
        self.__cohort = BModel.validate_number(cohort, "cohort")
        self.__token = token or secrets.token_urlsafe(32)
        self.token_state = token_state
        self.log_state = log_state
        self.__created_at = created_at or datetime.now()
        self.expires_at = expires_at

    @property
    def id(self):
        """Return the invitation unique id."""
        return self.__id

    @property
    def full_name(self):
        """Return the invited user's full name."""
        return self.__full_name

    @property
    def email(self):
        """Return the validated email address (lowercased)."""
        return self.__email

    @property
    def cohort(self):
        """Return the cohort number."""
        return self.__cohort

    @property
    def token(self):
        """Return the invitation token."""
        return self.__token

    @property
    def token_state(self):
        """Return whether the token has been used."""
        return self.__token_state

    @property
    def log_state(self):
        """Return whether the invited user completed registration."""
        return self.__log_state

    @property
    def created_at(self):
        """Return creation timestamp (UTC)."""
        return self.__created_at

    @property
    def expires_at(self):
        """Return expiration timestamp (UTC)."""
        return self.__expires_at

    # Setter for state change when token is used.
    @token_state.setter
    def token_state(self, value: bool):
        """
        Set token usage state.

        Args:
            value (bool): True if token was used, False otherwise.

        Raises:
            TypeError: if value is not a bool.
        """
        if not isinstance(value, bool):
            raise TypeError("Token state must be a boolean")
        self.__token_state = value

    # Setter for log if the user could registrate.
    @log_state.setter
    def log_state(self, value: bool):
        """
        Set registration log state.

        Args:
            value (bool): True if registration succeeded, False otherwise.

        Raises:
            TypeError: if value is not a bool.
        """
        if not isinstance(value, bool):
            raise TypeError("Log state must be a boolean")
        self.__log_state = value

    @expires_at.setter
    def expires_at(self, value: datetime | None):
        """
        Set the expiration date for the invitation.

        If value is falsy (e.g. None), generate a default expires_at = now + 30 days.
        """
        if not value:
            self.__expires_at = datetime.now() + timedelta(days=30)
            return
        if not isinstance(value, datetime):
            raise TypeError(f"Expires at must be a valid date")
        if value < self.created_at:
            raise ValueError("Expiration date must be after the creation date")

        self.__expires_at = value

    def is_valid(self) -> bool:
        """Check if invitation is valid (not expired and token not used)."""
        return not self.token_state and datetime.now(timezone.utc) <= self.expires_at

    def to_dict(self) -> dict:
        """
        Serialize the Invitation to a dictionary.
        Note: returns datetimes as datetime objects (PyMongo accepts these).
        """
        data = {
            "full_name": self.full_name,
            "email": self.email,
            "cohort": self.cohort,
            "token": self.token,
            "token_state": self.token_state,
            "log_state": self.log_state,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
        }

        if hasattr(self, f"_User__id"):
            data["id"] = self.id
        return data

    def __repr__(self):
        """Return a compact representation for debugging."""
        return f"Invitation(email={self.email}, cohort={self.cohort})"
