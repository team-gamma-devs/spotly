from pydantic import BaseModel, Field
from typing import List


class FiltersListResponse(BaseModel):
    filters: List[str] = Field(
        ..., description="List of possible technology filters available for querys"
    )


class FiltersPayload(BaseModel):
    pass
