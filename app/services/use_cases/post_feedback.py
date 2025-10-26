from typing import Any
import logging

from app.domain.models.user import User
from app.domain.models.tutorfeedback import TutorFeedback
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.services.exceptions.post_feedback_exceptions import InvalidFeedback

logger = logging.getLogger(__name__)


class PostFeedback:
    def __init__(
        self,
        user_repo: UserRepository = None,
    ):
        self.user_repo = user_repo or UserRepository()

    async def save_feedback(self, data: dict[str, Any]):
        graduated_id = data.pop("graduated_id")
        feedback = self._verify_feedback(data)
        user = await self._get_user(graduated_id)
        user.tutors_feedback_add(feedback.to_dict())

    def _verify_feedback(self, data: dict[str, Any]) -> TutorFeedback:
        try:
            feedback = TutorFeedback(**data)
        except (TypeError, ValueError) as e:
            raise InvalidFeedback(f"Feedback is invalid: {e}")

        return feedback

    async def _get_user(self, graduated_id: str) -> User:
        user = await self.user_repo.find_by_id(graduated_id)
        if not user:
            raise InvalidFeedback("Graduated id is invalid")
        return user

    async def _update_data(self, data: User):
        new_feedbacks = {"tutors_feedback": data.tutors_feedback}
        await self.user_repo.update(data.id, new_feedbacks)
