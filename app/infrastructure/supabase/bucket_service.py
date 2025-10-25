from fastapi import UploadFile
from typing import Optional, Dict
import uuid

from app.settings import settings
from app.domain.ports.supabase_storage_port import ISupabaseStorage
from app.infrastructure.supabase import supabase_client


class SupabaseStorageRepository(ISupabaseStorage):
    def __init__(self, client=supabase_client, bucket: str = settings.supabase_bucket):
        self.client = client
        self.bucket = bucket

    async def upload(self, file: UploadFile, folder: str) -> Dict[str, str]:
        ext = file.filename.split(".")[-1]
        path = f"{folder}/{uuid.uuid4()}.{ext}"
        data = await file.read()
        result = self.client.storage.from_(self.bucket).upload(path, data)
        if not result:
            raise Exception(result["error"]["message"])

        file_data = {
            "file_url": self.client.storage.from_(self.bucket).get_public_url(path),
            "file_path": str(result.path),
        }
        return file_data

    def delete(self, file_path: str) -> bool:
        res = self.client.storage.from_(self.bucket).remove([file_path])
        if res.get("error"):
            raise Exception(res["error"]["message"])
        return True
