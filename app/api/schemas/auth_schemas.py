from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    message: str
    access_token: str = Field(..., alias="accessToken")
    token_type: str = Field(..., aliad="tokenType")
    role: str

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True


class UserResponse(BaseModel):
    id: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    email: EmailStr
    avatar_url: str = Field(..., alias="avatarUrl")
    cohort: Optional[int] = None
    role: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
