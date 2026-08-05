from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Label, TaskLabel
from app.repositories.base import BaseRepository
from app.schemas.label import LabelCreate, LabelUpdate


class LabelRepository(BaseRepository[Label, LabelCreate, LabelUpdate]):

    async def get_by_project(self, db: AsyncSession, *, project_id: int) -> list[Label]:
        """Lấy tất cả label của một project."""
        stmt = select(Label).where(Label.project_id == project_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_for_project(
        self, db: AsyncSession, *, obj_in: LabelCreate, project_id: int
    ) -> Label:
        """Tạo label mới trong project."""
        db_obj = Label(
            project_id=project_id,
            name=obj_in.name,
            color=obj_in.color,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def add_label_to_task(
        self, db: AsyncSession, *, task_id: int, label_id: int
    ) -> bool:
        """Gắn label vào task."""
        # Kiểm tra đã gắn chưa
        stmt = select(TaskLabel).where(
            TaskLabel.task_id == task_id,
            TaskLabel.label_id == label_id,
        )
        result = await db.execute(stmt)
        if result.scalars().first():
            return False  # Đã tồn tại rồi

        db_obj = TaskLabel(task_id=task_id, label_id=label_id)
        db.add(db_obj)
        await db.commit()
        return True

    async def remove_label_from_task(
        self, db: AsyncSession, *, task_id: int, label_id: int
    ) -> bool:
        """Gỡ label khỏi task."""
        stmt = delete(TaskLabel).where(
            TaskLabel.task_id == task_id,
            TaskLabel.label_id == label_id,
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0


label_repo = LabelRepository(Label)
