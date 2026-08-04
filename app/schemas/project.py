from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ProjectStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["TaskHub Backend"])
    description: str | None = Field(None, max_length=1000)


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    status: ProjectStatus | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace_id: int
    name: str
    description: str | None = None
    status: str
    created_at: datetime
