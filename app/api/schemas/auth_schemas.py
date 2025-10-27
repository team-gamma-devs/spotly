from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr


class UserMe(BaseModel):
    id: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    role: str
    is_first_time: bool = Field(..., alias="isFirstTime")

    class Config:
        populate_by_name = True
        validate_by_name = True


class UserMe(BaseModel):
    id: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    role: str
    is_first_time: bool = Field(..., alias="isFirstTime")

    class Config:
        populate_by_name = True
        validate_by_name = True
