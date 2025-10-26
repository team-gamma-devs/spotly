from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    email: EmailStr


class UserMe(BaseModel):
    id: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    email: EmailStr
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    cohort: Optional[int] = None
    github: Optional[str] = None
    role: str
    is_first_time: bool = Field(..., alias="isFirstTime")
    created_at: datetime = Field(None, alias="createdAt")
    updated_at: datetime = Field(None, alias="updatedAt")

    class Config:
        populate_by_name = True
        validate_by_name = True
