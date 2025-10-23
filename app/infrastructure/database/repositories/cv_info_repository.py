from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any, List

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database import MongoDB


class CVInfoRepository(BaseRepository):
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """
        Invitation repository for CRUD operations on the 'invitations' collection.

        Args:
            db (AsyncIOMotorDatabase, optional): MongoDB database instance.
                Defaults to MongoDB.db singleton.
        """
        self.db = db or MongoDB.db
        collection = self.db["cvinfo"]
        super().__init__(collection)

    async def find_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find CVInfo by related user id."""
        return await self.find_one({"user_id": user_id})
