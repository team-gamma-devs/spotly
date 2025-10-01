from pydantic import BaseModel, Field
from typing import List

class StackItem(BaseModel):
    language: str
    size: int


class UserDataResponse(BaseModel):
    id: str
    username: str
    avatar_url: str = Field(..., alias="avatarUrl")
    stack: List[StackItem]

    class Config:
        populate_by_name = True
