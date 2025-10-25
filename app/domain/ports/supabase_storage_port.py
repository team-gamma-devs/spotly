from fastapi import UploadFile
from typing import Protocol, Optional


class ISupabaseStorage(Protocol):
    async def upload(self, file: UploadFile, folder: str) -> Optional[str]: ...

    async def delete(self, file_path: str) -> bool: ...
