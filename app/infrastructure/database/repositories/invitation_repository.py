from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any, List

from app.logger import get_logger
from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database import MongoDB

logger = get_logger(__name__)


class InvitationRepository(BaseRepository):
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """
        Invitation repository for CRUD operations on the 'invitations' collection.

        Args:
            db (AsyncIOMotorDatabase, optional): MongoDB database instance.
                Defaults to MongoDB.db singleton.
        """
        self.db = db or MongoDB.db  # <-- default to singleton if no db passed
        collection = self.db["invitations"]
        super().__init__(collection)

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find invitation by email."""
        try:
            doc = await self.find_one({"email": email})
            return doc
        except Exception as e:
            logger.exception(f"Error parsing invitation by token {email}: {e}")
            return None

    async def find_by_state(self, state: bool) -> List[Dict[str, Any]]:
        """Find all invitations by state."""
        return await self.find_all({"log_state": "False"})

    async def get_all_invitations(
        self, skip: int = 0, limit: int = 50
    ) -> List[dict[str, Any]]:
        invitations = await self.find_all({}, skip, limit)
        return invitations
