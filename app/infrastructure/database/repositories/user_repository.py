from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database import MongoDB


class UserRepository(BaseRepository):
    """
    Repository for performing CRUD operations on the 'users' collection in MongoDB.

    Inherits from BaseRepository and provides user-specific queries.
    """

    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """
        Initialize the UserRepository with a MongoDB database instance.

        Args:
            db (Optional[AsyncIOMotorDatabase]): Optional MongoDB database instance.
                If not provided, the default MongoDB.db singleton is used.
        """
        self.db = db or MongoDB.db
        collection = self.db["users"]
        super().__init__(collection)

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user document by email.

        Args:
            email (str): The email address of the user to search for.

        Returns:
            Optional[Dict[str, Any]]: The user document if found, otherwise None.
        """
        return await self.find_one({"email": email})

    async def user_email_exists(self, email: str) -> bool:
        """
        Check if a user exists with the given email.

        Args:
            email (str): The email address to check.

        Returns:
            bool: True if a user with the email exists, False otherwise.
        """
        doc = await self.find_one({"email": email})
        return doc is not None
