from typing import Optional, Any

from app.logger import get_logger
from app.domain.models.user import User
from app.infrastructure.database.repositories.user_repository import UserRepository

logger = get_logger(__name__)


class GraduatesFilter:
    """
    Use case to filter graduates based on technologies, English level, and tutor feedback.

    Attributes:
        user_repo (UserRepository): Repository to access user data.
    """

    def __init__(self, user_repo: Optional[UserRepository] = None):
        """
        Initialize the GraduatesFilter use case.

        Args:
            user_repo (UserRepository, optional): Custom user repository.
                Defaults to standard UserRepository.
        """
        self.user_repo = user_repo or UserRepository()

    async def process_filters(self, filters) -> list[dict[str, Any]]:
        """
        Process the filters and return a list of graduates matching the criteria.

        Args:
            filters: Object containing filtering criteria (technologies, English levels, tutors_feedback).

        Returns:
            list[dict[str, Any]]: List of graduates with serialized information.
        """
        filters = self._payload_serialization(filters)
        query = self._build_mongo_filters(filters)
        data = await self._process_query(query)
        response = self._serialization_for_response(data)
        return response

    def _payload_serialization(self, payload) -> dict[str, Any]:
        """
        Extract relevant fields from the incoming payload for filtering.

        Args:
            payload: Object containing the raw filter data.

        Returns:
            dict[str, Any]: Serialized filters containing 'technologies', 'english_levels', and 'feedbacks'.
        """
        techs = payload.technologies
        english_levels = [
            english_level.capitalize() for english_level in payload.english_levels
        ]
        feedbacks = payload.tutors_feedback
        filters = {}
        if english_levels:
            filters["english_levels"] = english_levels

        if techs:
            filters["technologies"] = techs

        if feedbacks:
            filters["feedbacks"] = feedbacks

        return filters

    def _build_mongo_filters(self, filters: dict[str, Any]) -> dict:
        """
        Build a MongoDB query dictionary based on the filters.

        Args:
            filters (dict[str, Any]): Serialized filters.

        Returns:
            dict: MongoDB query dictionary to filter graduates.
        """
        query = {}

        # Technologies
        if filters.get("technologies"):
            query["cv_info.skills"] = {"$all": filters["technologies"]}

        # English levels
        if filters.get("english_levels"):
            query["cv_info.english_level"] = {"$in": filters["english_levels"]}

        # Tutors feedback
        if filters.get("tutorsFeedback"):
            query["tutorsFeedback.tutor_id"] = {"$all": filters["tutorsFeedback"]}

        logger.info(f"{query}")

        return query

    async def _process_query(self, query: dict[str, Any]) -> list[User]:
        """
        Execute the database query and convert results to User instances.

        Args:
            query (dict[str, Any]): MongoDB query dictionary.

        Returns:
            list[User]: List of User model instances.
        """
        result = await self.user_repo.find_all(query)
        logger.info(f"{result}")
        graduates_list = [User(**graduate) for graduate in result]
        logger.info(f"{[user.to_dict() for user in graduates_list]}")
        return graduates_list

    def _serialization_for_response(
        self, graduates_list: list[User]
    ) -> list[dict[str, Any]]:
        """
        Serialize a list of User instances into dictionaries suitable for API response.

        Args:
            graduates_list (list[User]): List of User model instances.

        Returns:
            list[dict[str, Any]]: List of serialized graduate dictionaries.
        """
        response = []
        annotations = []
        general_feedback = {}
        for graduate in graduates_list:
            if graduate.tutors_feedback:
                annotations = [
                    feedback
                    for feedback in graduate.tutors_feedback
                    if feedback.get("annotations")
                ]

                general_feedback = {
                    feedback["id"]: {
                        "tutor_id": feedback["tutor_id"],
                        "created_at": feedback["created_at"],
                        "professional_score": feedback["professional_score"],
                        "technical_score": feedback["technical_score"],
                        "tutor_name": feedback["tutor_name"],
                    }
                    for feedback in graduate.tutors_feedback
                    if not feedback.get("annotations")
                }

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
                "github_url": graduate.github if graduate.github else "",
                "linkedin_url": graduate.cv_info["linkedin_url"],
                "created_at": graduate.created_at,
                "updated_at": graduate.updated_at,
                "annotations": annotations,
                "works_in_it": graduate.cv_info["works_in_it"],
                "tutors_feedback": general_feedback,
            }
            response.append(data)

        return response
