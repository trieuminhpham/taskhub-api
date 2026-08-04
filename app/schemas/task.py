from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(StrEnum):
    """Task status enum."""

    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    DONE = "DONE"


class TaskPriority(StrEnum):
    """Task priority enum."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


# --- Request Schemas ---


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=255, examples=["Fix login bug"])
    description: str | None = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: int | None = None
    due_date: date | None = None


class TaskUpdate(BaseModel):
    """Schema for updating a task (partial update)."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: int | None = None
    due_date: date | None = None


# --- Response Schemas ---


class TaskResponse(BaseModel):
    """Schema for task response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int | None = None
    assignee_id: int | None = None
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    due_date: date | None = None
    created_at: datetime
