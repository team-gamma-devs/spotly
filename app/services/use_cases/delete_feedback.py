from typing import Optional
from app.infrastructure.database.repositories.user_repository import (
    UserRepository,
)
from app.services.exceptions.delete_user_exceptions import DeleteError


class DeleteFeedback:
    """Service responsible for deleting invitations from the database."""

    def __init__(self, user_repo: Optional[UserRepository] = None):
        """
        Initialize the DeleteInvitation service.

        Args:
            invitation_repo (Optional[InvitationRepository]):
                Repository instance used to handle invitation deletion.
                If not provided, a new InvitationRepository instance will be created.
        """
        self.user_repo = user_repo or UserRepository()

    async def delete(self, payload: dict[str]) -> None:
        """
        Delete an invitation by its ID.

        Args:
            id (str): The unique identifier of the invitation to delete.

        Raises:
            DeleteError: If the deletion process fails.
        """
        success = await self.user_repo.delete(id)
        if not success:
            raise DeleteError("Invitation delete failed")
