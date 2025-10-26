from typing import Optional, Any

from app.logger import get_logger
from app.domain.models.user import User
from app.infrastructure.database.repositories.user_repository import UserRepository

logger = get_logger(__name__)


class GraduatesFilter:
    def __init__(self, user_repo: Optional[UserRepository] = None):
        self.user_repo = user_repo or UserRepository()

    async def process_filters(self, filters) -> list[dict[str, Any]]:
        filters = self._payload_serialization(filters)
        query = self._build_mongo_filters(filters)
        data = await self._process_query(query)
        response = self._serialization_for_response(data)
        return response

    def _payload_serialization(self, payload) -> dict[str, Any]:
        techs = payload.technologies
        english_levels = payload.english_levels
        feedbacks = payload.tutors_feedback
        filters = {
            "technologies": techs,
            "feedbacks": feedbacks,
            "english_levels": english_levels,
        }
        return filters

    def _build_mongo_filters(self, filters: dict[str, Any]) -> dict:
        query = {}

        # Tecnologías
        if filters.get("technologies"):
            query["cv_info.skills"] = {"$all": filters["technologies"]}

        # Nivel de inglés
        if filters.get("english_levels"):
            query["cv_info.english_level"] = {"$in": filters["english_levels"]}

        # Feedback de tutores
        if filters.get("tutorsFeedback"):
            query["tutorsFeedback"] = {"$all": filters["tutorsFeedback"]}

        logger.info(f"{query}")

        return query

    async def _process_query(self, query: dict[str, Any]) -> list[User]:
        result = await self.user_repo.find_all(query)
        logger.info(f"{result}")
        graduates_list = [User(**graduate) for graduate in result]
        logger.info(f"{[user.to_dict() for user in graduates_list]}")
        return graduates_list

    def _serialization_for_response(
        self, graduates_list: list[User]
    ) -> list[dict[str, Any]]:
        response = []
        annotations = None
        general_feedback = None
        for graduate in graduates_list:
            if graduate.tutors_feedback:
                annotations = [
                    feedback
                    for feedback in graduate.tutors_feedback
                    if feedback.get("annotations")
                ]

                general_feedback = [
                    feedback
                    for feedback in graduate.tutors_feedback
                    if not feedback.get("annotations")
                ]

            data = {
                "id": graduate.id,
                "first_name": graduate.first_name,
                "last_name": graduate.last_name,
                "email": graduate.email,
                "cv_url": graduate.cv_info["personal_cv_url"],
                "english_level": graduate.cv_info["english_level"],
                "avatar_url": graduate.avatar_url,
                "cohort": graduate.cohort,
                "tech_stack": graduate.cv_info["skills"],
                "github_url": graduate.github,
                "linkedin_url": graduate.cv_info["linkedin_url"],
                "created_at": graduate.created_at,
                "updated_at": graduate.updated_at,
                "annotations": annotations,
                "tutors_feedback": general_feedback,
            }
            response.append(data)

        return response
