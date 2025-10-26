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

    def __init__(self, invitations_repo: Optional[InvitationRepository] = None):
        """
        Initialize the GetInvitations use case.

        Args:
            invitations_repo (Optional[InvitationRepository]):
                Custom invitation repository. Defaults to standard InvitationRepository.
        """
        self.invitations_repo = invitations_repo or InvitationRepository()

    async def get_all_invitations(
        self, skip: int = 0, limit: int = 50
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
        invitations = await self.invitations_repo.get_all_invitations(skip, limit)
        pages = math.ceil(await self.invitations_repo.count({}) / limit)
        result = {
            "items": invitations,
            "pages": pages,
            "page": (skip // limit) + 1,
            "limit": limit,
        }
        return result
