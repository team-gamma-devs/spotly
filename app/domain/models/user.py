from datetime import datetime
import re
from typing import Optional, List, Dict, Any

from app.domain.models.bmodel import BModel


class User(BModel):
    """
    Represents a user in the system.

    Attributes:
        id (str | None): Unique identifier (ObjectId).
        first_name (str): User's first name (validated, readonly).
        last_name (str): User's last name (validated, readonly).
        email (str): User's email (validated, readonly).
        avatar_url (str): URL of the user's avatar image.
        avatar_path (str): File path of the user's avatar image.
        cohort (int | None): Cohort number.
        github_url (str | None): GitHub username or URL.
        cv_info (dict | None): Dictionary containing CV information.
        tutors_feedback (List[dict] | None): List of feedback entries from tutors.
        role (str): Role of the user (default: "graduate").
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
    """

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        avatar_url: str,
        avatar_path: str,
        id: Optional[str] = None,
        cohort: Optional[int] = None,
        github_url: Optional[str] = None,
        cv_info: Optional[dict] = None,
        tutors_feedback: Optional[List[Dict[str, Any]]] = None,
        role: str = "graduate",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """
        Initialize a User instance.

        Args:
            first_name (str): User's first name.
            last_name (str): User's last name.
            email (str): User's email address.
            avatar_url (str): URL of the user's avatar.
            avatar_path (str): File path of the user's avatar.
            id (str | None): Optional database ID.
            cohort (int | None): Optional cohort number.
            github_url (str | None): Optional GitHub profile.
            cv_info (dict | None): Optional CV info dictionary.
            tutors_feedback (List[str] | None): Optional list of tutor feedback.
            role (str): Role of the user, defaults to "graduate".
            created_at (datetime | None): Optional creation timestamp.
            updated_at (datetime | None): Optional last update timestamp.
        """
        super().__init__(id, created_at, updated_at)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.cohort = cohort
        self.avatar_url = avatar_url
        self.avatar_path = avatar_path
        self.github_url = github_url
        self.cv_info = cv_info
        self.tutors_feedback = tutors_feedback
        self.__role = role

    # -------------------- Properties -------------------- #

    @property
    def first_name(self):
        """Return the user's first name."""
        return self.__first_name

    @property
    def last_name(self):
        """Return the user's last name."""
        return self.__last_name

    @property
    def email(self):
        """Return the user's validated email address."""
        return self.__email

    @property
    def cohort(self):
        """Return the user's cohort number, if set."""
        return self.__cohort

    @property
    def avatar_url(self):
        """Return the URL of the user's avatar."""
        return self.__avatar_url

    @property
    def avatar_path(self):
        """Return the file path of the user's avatar."""
        return self.__avatar_path

    @property
    def github_url(self):
        """Return the user's GitHub profile (URL or username)."""
        return self.__github

    @property
    def cv_info(self):
        """Return the user's CV information dictionary."""
        return self.__cv_info

    @property
    def tutors_feedback(self):
        """Return the list of tutor feedback entries."""
        return self._tutors_feedback

    @property
    def role(self):
        """Return the user's role."""
        return self.__role

    # -------------------- Setters -------------------- #

    @first_name.setter
    def first_name(self, value: str):
        """Validate and set the user's first name (letters only)."""
        self.__first_name = self.validate_alpha(value, "first_name")

    @last_name.setter
    def last_name(self, value: str):
        """Validate and set the user's last name (letters only)."""
        self.__last_name = self.validate_alpha(value, "last_name")

    @email.setter
    def email(self, value: str):
        """Validate and set the user's email address."""
        self.__email = BModel.validate_email(value)

    @cohort.setter
    def cohort(self, value: Optional[int]):
        """Validate and set the user's cohort number (optional)."""
        if not value:
            self.__cohort = None
        else:
            self.__cohort = BModel.validate_number(value, "Cohort")

    @github_url.setter
    def github_url(self, value: Optional[str]):
        """Validate and set the user's GitHub profile (optional)."""
        if not value:
            self.__github = None
        else:
            self.__github = BModel.validate_string(value, "github_url")

    @avatar_url.setter
    def avatar_url(self, value: str):
        """Validate and set the user's avatar URL."""
        self.__avatar_url = BModel.validate_url(value, "avatar_url")

    @avatar_path.setter
    def avatar_path(self, value: str):
        """Validate and set the user's avatar file path."""
        self.__avatar_path = BModel.validate_string(value, "avatar_path")

    @cv_info.setter
    def cv_info(self, value: Optional[dict]):
        """Validate and set the user's CV info dictionary (optional)."""
        if not value:
            self.__cv_info = None
            return
        if not isinstance(value, dict):
            raise Exception("cv_info must be a dict")
        self.__cv_info = value

    @tutors_feedback.setter
    def tutors_feedback(self, value: Optional[list[dict[str, Any]]]):
        """Validate and set the user's tutors feedback list (optional)."""
        if not value:
            self._tutors_feedback = None
            return
        if not isinstance(value, list):
            raise ValueError(f"{value} must be a list of feedbacks")
        self._tutors_feedback = value

    # -------------------- Methods -------------------- #

    def tutors_feedback_add(self, feedback: Dict[str, Any]):
        """
        Add a new feedback entry to the user's tutor feedback list.

        Args:
            feedback (dict): Dictionary containing feedback details.

        Raises:
            TypeError: If feedback is not a dictionary.
        """
        if not isinstance(feedback, dict):
            raise TypeError("Invalid Feedback")

        if not self.tutors_feedback:
            self.tutors_feedback = [feedback]
        else:
            self.tutors_feedback = self.tutors_feedback + [feedback]

    def to_dict(self) -> dict:
        """
        Serialize the User instance to a dictionary.

        Returns:
            dict: Dictionary containing all user attributes and optional fields.
        """
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
        if self.github_url:
            data["github_url"] = self.github_url
        if self.cv_info:
            data["cv_info"] = self.cv_info
        if self.tutors_feedback:
            data["tutors_feedback"] = self.tutors_feedback
        if self.cohort:
            data["cohort"] = self.cohort

        return data

    @staticmethod
    def validate_alpha(value: str, field_name: str) -> str:
        """
        Validate that a string contains only letters (optionally one hyphen or apostrophe).

        Args:
            value (str): Value to validate.
            field_name (str): Field name for error messages.

        Returns:
            str: Validated string.

        Raises:
            ValueError: If string contains invalid characters.
        """
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
        """Return a compact representation for debugging purposes."""
        return (
            f"first_name={self.first_name!r}, last_name={self.last_name!r}, "
            f"email={self.email!r}, role={self.role!r})"
        )
