from pydantic import BaseModel, Field, EmailStr, AnyUrl
from datetime import datetime
from typing import Optional, Literal


class FiltersListResponse(BaseModel):
    filters: list[str] = Field(
        ..., description="List of possible technology filters available for querys"
    )


class FiltersPayload(BaseModel):
    technologies: Optional[list[str]] = Field(
        None, description="List of technologies that graduates must have"
    )
    english_levels: Optional[list[Literal["basic", "intermediate", "advanced"]]] = (
        Field(
            None,
            alias="englishLevels",
            description="Minimum level of English that the graduate must have",
        )
    )
    tutors_feedback: Optional[list[str]] = Field(
        None,
        alias="tutorsFeedback",
        description="Tutors name feedbacks that graduate must have",
    )

    class Config:
        populate_by_name = True
        validate_by_name = True


# Filtered Users Response Model
class Annotations(BaseModel):
    created_at: datetime = Field(
        ...,
        alias="createdAt",
        description="Timestamp when the annotation was created.",
    )
    message: str = Field(
        ...,
        description="Message or note attached to the user profile or feedback.",
    )

    class Config:
        populate_by_name = True
        validate_by_name = True


class FilteredUsers(BaseModel):
    id: str = Field(
        ...,
        description="Unique identifier of the user.",
    )
    first_name: str = Field(
        ...,
        alias="firstName",
        description="User's first name.",
    )
    last_name: str = Field(
        ...,
        alias="lastName",
        description="User's last name.",
    )
    email: EmailStr = Field(
        ...,
        description="User's email address. Must be a valid email format.",
    )
    cv_url: AnyUrl = Field(
        ..., alias="cvUrl", description="Public URL of the user's personal cv"
    )
    english_level: Literal["basic", "intermediate", "advanced"] = Field(
        ..., alias="englishLevel", description="User's english level"
    )
    avatar_url: AnyUrl = Field(
        ...,
        alias="avatarUrl",
        description="Public URL of the user's avatar image.",
    )
    cohort: int = Field(
        ...,
        description="Cohort number the user belongs to.",
    )
    tech_stack: list[str] = Field(
        ...,
        alias="techStack",
        description="List of technologies the user works with.",
    )
    github_url: Optional[AnyUrl] = Field(
        None,
        alias="githubUrl",
        description="User's GitHub profile URL, if available.",
    )
    linkedin_url: AnyUrl = Field(
        ...,
        alias="linkedinUrl",
        description="User's LinkedIn profile URL.",
    )
    annotations: Optional[Annotations] = Field(
        None,
        description="Metadata or comments associated with the user.",
    )
    tutors_feedback: Optional[list[dict]] = Field(
        None,
        alias="tutorsFeedback",
        description="Dictionary containing tutor feedback data for the user.",
    )
    created_at: datetime = Field(
        ..., alias="createdAt", description="Timestamp of the user creation date"
    )
    updated_at: datetime = Field(
        ...,
        alias="updatedAt",
        description="Timestamp of the last user data update",
    )

    class Config:
        populate_by_name = True
        validate_by_name = True
