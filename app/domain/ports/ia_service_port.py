from typing import Protocol


class IAService(Protocol):
    async def parse_text(self, text: str) -> dict: ...

    async def parse_file(self, file_bytes: bytes, filename: str) -> dict: ...
