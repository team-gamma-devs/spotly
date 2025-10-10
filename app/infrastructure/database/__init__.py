from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None

    @classmethod
    async def connect_db(cls, mongodb_url: str, database_name: str):
        """Connect to MongoDB"""
        cls.client = AsyncIOMotorClient(mongodb_url)
        return cls.client[database_name]

    @classmethod
    async def close_db(cls):
        """Close conection to MongoDB"""
        if cls.client:
            cls.client.close()
