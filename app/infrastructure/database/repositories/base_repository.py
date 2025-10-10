from typing import Generic, Type, TypeVar, List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, collection: AsyncIOMotorCollection, model: Type[T]):
        self.collection = collection
        self.model = model

    def _to_dict(self, entity: T) -> dict:
        """Convert domain object to Mongo document."""
        data = entity.to_dict().copy()
        data["_id"] = ObjectId(data.pop("id"))
        return data

    def _from_dict(self, data: dict) -> T:
        """Convert Mongo document to domain object."""
        if not data:
            return None
        data["id"] = str(data.pop("_id"))
        return self.model(**data)

    async def create(self, entity: T) -> str:
        doc = self._to_dict(entity)
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def find_by_id(self, id_: str) -> Optional[T]:
        data = await self.collection.find_one({"_id": ObjectId(id_)})
        return self._from_dict(data)

    async def find_all(self, filters: dict = None) -> List[T]:
        cursor = self.collection.find(filters or {})
        return [self._from_dict(doc) async for doc in cursor]

    async def update(self, id_: str, updates: dict) -> bool:
        """Updates specific fields, returns True if modified."""
        result = await self.collection.update_one(
            {"_id": ObjectId(id_)}, {"$set": updates}
        )
        return result.modified_count > 0

    async def delete(self, id_: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id_)})
        return result.deleted_count > 0
