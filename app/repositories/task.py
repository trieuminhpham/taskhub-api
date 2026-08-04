from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Task
from app.repositories.base import BaseRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):

    async def get_by_project(
        self, db: AsyncSession, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> list[Task]:
        """Lấy danh sách task thuộc một project."""
        stmt = select(Task).where(Task.project_id == project_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_in_project(
        self, db: AsyncSession, *, obj_in: TaskCreate, project_id: int, created_by: int
    ) -> Task:
        """Tạo task trong một project cụ thể."""
        db_obj = Task(
            project_id=project_id,
            title=obj_in.title,
            description=obj_in.description,
            status=obj_in.status,
            priority=obj_in.priority,
            assignee_id=obj_in.assignee_id,
            due_date=obj_in.due_date,
            created_by=created_by,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


task_repo = TaskRepository(Task)
