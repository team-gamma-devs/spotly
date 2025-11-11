from typing import Optional, Any
from app.infrastructure.database.repositories.user_repository import (
    UserRepository,
)
from app.domain.models.user import User


class GetIncompleteFeedbacks:
    def __init__(self, user_repo: Optional[UserRepository] = None):
        self.user_repo = user_repo or UserRepository()

    async def get_incomplete_feedbacks(self, user) -> list[dict[str, Any]]:
        tutor_id = await self._get_tutor_id(user.email)
        return await self._get_graduates_no_feedback(tutor_id)

    async def _get_graduates_no_feedback(
        self, tutor_id: str
    ) -> list[dict[str, Any]]:
        users_without_feedback = await self.user_repo.find_all(
            {
                "$or": [
                    {"tutors_feedback": {"$exists": False}},
                    {
                        "tutors_feedback": {
                            "$not": {"$elemMatch": {"tutor_id": tutor_id}}
                        }
                    },
                ]
            }
        )
        result = []
        for graduate in users_without_feedback:
            graduate = User(**graduate)
            data = {
                "id": graduate.id,
                "first_name": graduate.first_name,
                "last_name": graduate.last_name,
                "cohort": graduate.cohort,
            }
            result.append(data)

        return result

    async def _get_tutor_id(self, email: str) -> str:
        tutor = await self.user_repo.find_by_email(email)
        return tutor["id"]
