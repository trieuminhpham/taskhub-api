from enum import StrEnum

from fastapi import Query
from pydantic import BaseModel


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class TaskFilter(BaseModel):
    """Query parameters để filter danh sách Task."""

    status: str | None = Query(default=None, examples=["TODO", "IN_PROGRESS", "IN_REVIEW", "DONE"])
    priority: str | None = Query(default=None, examples=["LOW", "MEDIUM", "HIGH", "URGENT"])
    assignee_id: int | None = Query(default=None)
    search: str | None = Query(default=None, description="Tìm kiếm theo title của task")
    skip: int = Query(default=0, ge=0)
    limit: int = Query(default=20, ge=1, le=100)


class ProjectFilter(BaseModel):
    """Query parameters để filter danh sách Project."""

    status: str | None = Query(default=None, examples=["ACTIVE", "ARCHIVED"])
    search: str | None = Query(default=None, description="Tìm kiếm theo tên project")
    skip: int = Query(default=0, ge=0)
    limit: int = Query(default=20, ge=1, le=100)
