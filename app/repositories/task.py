from sqlalchemy import or_, select
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

    async def get_filtered(
        self,
        db: AsyncSession,
        *,
        project_id: int,
        status: str | None = None,
        priority: str | None = None,
        assignee_id: int | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Task]:
        """Lọc task theo nhiều điều kiện, hỗ trợ tìm kiếm và phân trang."""
        stmt = select(Task).where(Task.project_id == project_id)
        # Filter theo status
        if status:
            stmt = stmt.where(Task.status == status)
        # Filter theo priority
        if priority:
            stmt = stmt.where(Task.priority == priority)
        # Filter theo assignee
        if assignee_id:
            stmt = stmt.where(Task.assignee_id == assignee_id)
        # Tìm kiếm theo title hoặc description
        if search:
            stmt = stmt.where(
                or_(
                    Task.title.ilike(f"%{search}%"),
                    Task.description.ilike(f"%{search}%"),
                )
            )
        # Sắp xếp mới nhất lên trên
        stmt = stmt.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


task_repo = TaskRepository(Task)
