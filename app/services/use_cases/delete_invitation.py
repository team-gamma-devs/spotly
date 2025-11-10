from typing import Optional
from app.infrastructure.database.repositories.invitation_repository import (
    InvitationRepository,
)
from app.services.exceptions.delete_user_exceptions import DeleteError


class DeleteInvitation:
    """Service responsible for deleting invitations from the database."""

    def __init__(self, invitation_repo: Optional[InvitationRepository] = None):
        """
        Initialize the DeleteInvitation service.

        Args:
            invitation_repo (Optional[InvitationRepository]):
                Repository instance used to handle invitation deletion.
                If not provided, a new InvitationRepository instance will be created.
        """
        self.invitation_repo = invitation_repo or InvitationRepository()

    async def delete(self, id: str) -> None:
        """
        Delete an invitation by its ID.

        Args:
            id (str): The unique identifier of the invitation to delete.

        Raises:
            DeleteError: If the deletion process fails.
        """
        success = await self.invitation_repo.delete(id)
        if not success:
            raise DeleteError("Invitation delete failed")
