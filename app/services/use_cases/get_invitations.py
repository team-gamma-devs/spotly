from typing import Optional, List, Any
import math
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)


class GetInvitations:
    """
    Use case to fetch paginated invitations from the database.

    Attributes:
        invitations_repo (InvitationRepository): Repository to access invitation data.
    """

    def __init__(
        self, invitations_repo: Optional[InvitationRepository] = None
    ):
        """
        Initialize the GetInvitations use case.

        Args:
            invitations_repo (Optional[InvitationRepository]):
                Custom invitation repository. Defaults to standard InvitationRepository.
        """
        self.invitations_repo = invitations_repo or InvitationRepository()

    async def get_invitations(
        self, payload, page: int = 1, page_size: int = 50
    ) -> dict[str, Any]:
        """
        Retrieve invitations with pagination information.

        Args:
            skip (int): Number of invitations to skip (for pagination). Defaults to 0.
            limit (int): Maximum number of invitations to return. Defaults to 50.

        Returns:
            dict[str, Any]: A dictionary containing:
                - "items": List of invitations.
                - "pages": Total number of pages.
                - "page": Current page number (1-based).
                - "limit": Limit per page.
        """
        query = self._generate_query(payload)
        result = await self._execute_query(query, page, page_size)
        return result

    def _generate_query(self, payload) -> dict[str, Any]:
        search_term = search_term = (payload.search_param or "").strip()
        if not search_term:
            return {}

        query = {
            "$or": [
                {"full_name": {"$regex": search_term, "$options": "i"}},
                {"email": {"$regex": search_term, "$options": "i"}},
            ]
        }

        return query

    async def _execute_query(
        self, query: dict[str, Any], page: int = 1, page_size: int = 50
    ) -> dict[str, Any]:
        skip = (page - 1) * page_size
        limit = page_size
        invitations = await self.invitations_repo.find_all(query, skip, limit)
        pages = math.ceil(await self.invitations_repo.count(query) / limit)
        result = {
            "items": invitations,
            "pages": pages,
            "page": (skip // limit) + 1,
            "limit": limit,
        }

        return result
