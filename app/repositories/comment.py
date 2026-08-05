from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Comment
from app.repositories.base import BaseRepository
from app.schemas.comment import CommentCreate, CommentUpdate


class CommentRepository(BaseRepository[Comment, CommentCreate, CommentUpdate]):

    async def get_by_task(self, db: AsyncSession, *, task_id: int) -> list[Comment]:
        """Lấy tất cả bình luận của một task."""
        stmt = select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_for_task(
        self, db: AsyncSession, *, obj_in: CommentCreate, task_id: int, author_id: int
    ) -> Comment:
        """Tạo bình luận mới cho task."""
        db_obj = Comment(
            task_id=task_id,
            author_id=author_id,
            content=obj_in.content,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


comment_repo = CommentRepository(Comment)
