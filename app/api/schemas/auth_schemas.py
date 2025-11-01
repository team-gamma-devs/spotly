from pydantic import BaseModel, EmailStr, Field, AnyUrl
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    email: EmailStr


class UserMe(BaseModel):
    id: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    role: str
    is_first_time: bool = Field(..., alias="isFirstTime")

    class Config:
        populate_by_name = True
        validate_by_name = True


class CVInfoModel(BaseModel):
    personal_cv_url: AnyUrl = Field(..., alias="personalCvUrl")
    linkedin_url: AnyUrl = Field(..., alias="linkedinUrl")
    skills: list[str]
    english_level: str = Field(..., alias="englishLevel")
    works_in_it: bool = Field(..., alias="worksInIt")
    last_update: datetime = Field(..., alias="lastUpdate")

    class Config:
        populate_by_name = True
        validate_by_name = True


class TutorsFeedbackModel(BaseModel):
    id: str
    tutor_id: str = Field(..., alias="tutorId")
    tutor_name: str = Field(..., alias="tutorName")
    professional_score: Optional[str] = Field(None, alias="professionalScore")
    technical_score: Optional[str] = Field(None, alias="technicalScore")
    annotation: Optional[str]
    created_at: datetime

    class Config:
        populate_by_name = True
        validate_by_name = True


class UserMeFull(BaseModel):
    id: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    email: EmailStr
    avatar_url: AnyUrl
    cohort: Optional[int]
    github: Optional[str]
    cv_info: Optional[CVInfoModel] = Field(None, alias="cvInfo")
    tutors_feedback: Optional[list[TutorsFeedbackModel]] = Field(
        None, alias="tutorsFeedback"
    )
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        validate_by_name = True
