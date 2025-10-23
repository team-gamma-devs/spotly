from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database import MongoDB


class FiltersRepository(BaseRepository):
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """
        Repository for managing filters in the 'filters' collection.

        Args:
            db (Optional[AsyncIOMotorDatabase]): MongoDB database instance.
                If not provided, defaults to the MongoDB.db singleton.
        """
        self.db = db or MongoDB.db
        collection = self.db["filters"]
        super().__init__(collection)

    async def add_user_filters(self, user_filters: List[str]):
        """
        Add new filters from a user's technologies to the collection.

        This method updates the single document in the 'filters' collection
        by adding only new, non-duplicated filters. If the document does not
        exist yet, it will be created automatically.

        Args:
            user_filters (List[str]): List of technologies/filters from the user.
        """
        result = await self.collection.update_one(
            {},
            {"$addToSet": {"available_filters": {"$each": user_filters}}},
            upsert=True,
        )
        return result.matched_count

    async def get_filters(self) -> List[str]:
        """
        Retrieve the list of available filters.

        This method fetches the unique document in the 'filters' collection
        and returns its 'available_filters' array. If no document exists yet,
        it returns an empty list.

        Returns:
            List[str]: List of available filters.
        """
        doc = await self.collection.find_one({}, {"_id": 0, "available_filters": 1})
        return doc["available_filters"] if doc else []
