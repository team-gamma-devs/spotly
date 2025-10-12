from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId


class BaseRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    def _to_mongo_doc(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert dict with 'id' to MongoDB document with '_id'."""
        doc = data.copy()
        if "id" in doc:
            doc["_id"] = ObjectId(doc.pop("id"))
        return doc

    def _from_mongo_doc(
        self, doc: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Convert MongoDB document with '_id' to dict with 'id'."""
        if not doc:
            return None
        result = doc.copy()
        result["id"] = str(result.pop("_id"))
        return result

    async def create(self, data: Dict[str, Any]) -> str:
        """Create a new document and return its ID."""
        doc = self._to_mongo_doc(data)
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def find_by_id(self, id_: str) -> Optional[Dict[str, Any]]:
        """Find document by ID, returns dict or None."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(id_)})
            return self._from_mongo_doc(doc)
        except Exception:
            return None

    async def find_all(
        self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find all documents matching filters."""
        cursor = self.collection.find(filters or {}).skip(skip).limit(limit)
        return [self._from_mongo_doc(doc) async for doc in cursor]

    async def find_one(self, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document matching filters."""
        doc = await self.collection.find_one(filters)
        return self._from_mongo_doc(doc)

    async def update(self, id_: str, updates: Dict[str, Any]) -> bool:
        """Update specific fields, returns True if modified."""
        try:
            # Remove 'id' if present in updates to avoid conflicts
            clean_updates = {k: v for k, v in updates.items() if k != "id"}
            result = await self.collection.update_one(
                {"_id": ObjectId(id_)}, {"$set": clean_updates}
            )
            return result.modified_count > 0
        except Exception:
            return False

    async def delete(self, id_: str) -> bool:
        """Delete document by ID."""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(id_)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def exists(self, id_: str) -> bool:
        """Check if document exists."""
        try:
            count = await self.collection.count_documents(
                {"_id": ObjectId(id_)}, limit=1
            )
            return count > 0
        except Exception:
            return False

    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count documents matching filters."""
        return await self.collection.count_documents(filters or {})
