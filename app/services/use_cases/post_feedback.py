from typing import Any

from app.logger import get_logger
from app.domain.models.user import User
from app.domain.models.tutorfeedback import TutorFeedback
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.services.exceptions.post_feedback_exceptions import InvalidFeedback

logger = get_logger(__name__)


class PostFeedback:
    """
    Use case for posting tutor feedback to a graduate.

    Attributes:
        user_repo (UserRepository): Repository to access and update user data.
    """

    def __init__(
        self,
        user_repo: UserRepository = None,
    ):
        """
        Initialize the PostFeedback use case.

        Args:
            user_repo (UserRepository, optional): Custom user repository.
                Defaults to standard UserRepository.
        """
        self.user_repo = user_repo or UserRepository()

    async def save_feedback(self, data, user: dict[str, Any]):
        """
        Save a tutor feedback entry for a specific graduate.

        Args:
            data: FeedbackSchema object containing feedback data.
            user: Dictionary containing user information from JWT.

        Raises:
            InvalidFeedback: If the feedback is invalid or the graduated_id does not exist.
        """
        graduated_id = data.graduated_id

        tutor = await self._get_tutor(user["email"])

        feedback_dict = {
            "annotation": data.annotation,
            "technical_score": data.technical_score,
            "professional_score": data.professional_score,
        }

        feedback = self._generate_feedback(feedback_dict, tutor)
        graduated = await self._get_user(graduated_id)
        graduated.tutors_feedback_add(feedback.to_dict())
        await self._update_data(graduated)

    def _generate_feedback(self, data: dict[str, Any], tutor: User) -> TutorFeedback:
        """
        Verify and validate the feedback data.

        Args:
            data (dict[str, Any]): Feedback data.

        Returns:
            TutorFeedback: Validated TutorFeedback instance.

        Raises:
            InvalidFeedback: If the feedback data cannot be used to instantiate a TutorFeedback.
        """
        data["tutor_id"] = tutor.id
        data["tutor_name"] = tutor.first_name + " " + tutor.last_name
        try:
            feedback = TutorFeedback(**data)
        except (TypeError, ValueError) as e:
            raise InvalidFeedback(f"Feedback is invalid: {e}")

        return feedback

    async def _get_user(self, graduated_id: str) -> User:
        """
        Retrieve a graduate user by ID.

        Args:
            graduated_id (str): ID of the graduate.

        Returns:
            User: User instance corresponding to the graduate.

        Raises:
            InvalidFeedback: If no user is found with the provided ID.
        """
        user = await self.user_repo.find_by_id(graduated_id)
        if not user:
            raise InvalidFeedback("Graduated id is invalid")
        return User(**user)

    async def _get_tutor(self, tutor_email: str) -> User:
        tutor = await self.user_repo.find_by_email(tutor_email)
        if not tutor:
            raise InvalidFeedback("Invalid tutor")
        return User(**tutor)

    async def _update_data(self, data: User):
        """
        Persist the updated tutor feedback list to the database.

        Args:
            data (User): User instance with updated tutor feedback.
        """
        new_feedback = {"tutors_feedback": data.tutors_feedback}
        result = await self.user_repo.update(data.id, new_feedback)
