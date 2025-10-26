from typing import Optional, List, Any
import math
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)


class GetInvitations:
    def __init__(self, invitations_repo: Optional[InvitationRepository] = None):
        self.invitations_repo = invitations_repo or InvitationRepository()

    async def get_all_invitations(
        self, skip: int = 0, limit: int = 50
    ) -> List[dict[str, Any]]:
        invitations = await self.invitations_repo.get_all_invitations(skip, limit)
        pages = math.ceil(await self.invitations_repo.count({}) / limit)
        result = {
            "items": invitations,
            "pages": pages,
            "page": (skip // limit) + 1,
            "limit": limit,
        }
        return result
