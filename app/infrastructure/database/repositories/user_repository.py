from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any, List

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database import MongoDB


class UserRepository(BaseRepository):
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """
        Invitation repository for CRUD operations on the 'invitations' collection.

        Args:
            db (AsyncIOMotorDatabase, optional): MongoDB database instance.
                Defaults to MongoDB.db singleton.
        """
        self.db = db or MongoDB.db
        collection = self.db["users"]
        super().__init__(collection)

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find User by email."""
        return await self.find_one({"email": email})

    async def find_by_state(self, state: bool) -> List[Dict[str, Any]]:
        """Find all invitations by state."""
        return await self.find_all({"log_state": "False"})
