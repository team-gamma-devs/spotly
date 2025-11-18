from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime


class LoginRequest(BaseModel):
    email: EmailStr


class UserMe(BaseModel):
    """Matches frontend UserMe type from userMe.ts"""

    model_config = ConfigDict(validate_by_name=True)

    id: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    role: Literal["graduate", "manager"]
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    is_first_time: bool = Field(..., alias="isFirstTime")


class CVInfoModel(BaseModel):
    """Matches frontend CvInfo interface from userFull.ts"""

    model_config = ConfigDict(validate_by_name=True)

    personal_cv_url: str = Field(..., alias="personalCvUrl")
    linkedin_url: str = Field(..., alias="linkedinUrl")
    skills: list[str]
    english_level: Literal["Basic", "Intermediate", "Advanced"] = Field(
        ..., alias="englishLevel"
    )
    works_in_it: bool = Field(..., alias="worksInIt")
    last_update: datetime = Field(..., alias="lastUpdate")


class TutorsFeedbackModel(BaseModel):
    """Matches frontend TutorFeedback interface from userFull.ts"""

    model_config = ConfigDict(validate_by_name=True)

    id: str
    tutor_id: str = Field(..., alias="tutorId")
    tutor_name: str = Field(..., alias="tutorName")
    professional_score: Optional[str] = Field(None, alias="professionalScore")
    technical_score: Optional[str] = Field(None, alias="technicalScore")
    annotation: Optional[str] = None
    created_at: datetime = Field(..., alias="createdAt")


class UserMeFull(BaseModel):
    """Matches frontend UserState interface from userFull.ts"""

    model_config = ConfigDict(validate_by_name=True)

    id: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    email: EmailStr
    avatar_url: str = Field(..., alias="avatarUrl")
    cohort: int
    github_url: Optional[str] = Field(None, alias="githubUrl")
    cv_info: CVInfoModel = Field(..., alias="cvInfo")
    tutors_feedback: list[TutorsFeedbackModel] = Field(
        default=[], alias="tutorsFeedback"
    )
    role: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
