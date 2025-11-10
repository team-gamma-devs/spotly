from fastapi import UploadFile
from typing import Dict
import uuid

from app.settings import settings
from app.domain.ports.supabase_storage_port import ISupabaseStorage
from app.infrastructure.supabase import supabase_client


class SupabaseStorageRepository(ISupabaseStorage):
    """
    Supabase storage repository implementation for file upload and deletion.

    Attributes:
        client: Supabase client instance.
        bucket (str): Supabase storage bucket name.
    """

    def __init__(self, client=supabase_client, bucket: str = settings.supabase_bucket):
        """
        Initialize the SupabaseStorageRepository.

        Args:
            client: Supabase client instance. Defaults to `supabase_client`.
            bucket (str): Bucket name for storage. Defaults to settings.supabase_bucket.
        """
        self.client = client
        self.bucket = bucket

    async def upload(self, file: UploadFile, folder: str) -> Dict[str, str]:
        """
        Upload a file to Supabase storage in the specified folder.

        Args:
            file (UploadFile): File to upload.
            folder (str): Folder path inside the bucket where the file will be stored.

        Returns:
            dict: Dictionary containing:
                - file_url (str): Public URL of the uploaded file.
                - file_path (str): Internal path of the uploaded file in the bucket.

        Raises:
            Exception: If upload fails, raises with the error message from Supabase.
        """
        ext = file.filename.split(".")[-1]
        path = f"{folder}/{uuid.uuid4()}.{ext}"
        data = await file.read()
        result = self.client.storage.from_(self.bucket).upload(path, data)
        if not result:
            raise Exception(result["error"]["message"])

        file_data = {
            "file_url": self.client.storage.from_(self.bucket).get_public_url(path),
            "file_path": "/" + "/".join(result.path),
        }
        return file_data

    def delete(self, file_path: str) -> bool:
        """
        Delete a file from Supabase storage.

        Args:
            file_path (str): Internal path of the file to delete.

        Returns:
            bool: True if deletion was successful.

        Raises:
            Exception: If deletion fails, raises with the error message from Supabase.
        """
        res = self.client.storage.from_(self.bucket).remove([file_path])
        if res.get("error"):
            raise Exception(res["error"]["message"])
        return True
