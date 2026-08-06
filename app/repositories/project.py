from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Project
from app.repositories.base import BaseRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectUpdate]):

    async def get_by_workspace(self, db: AsyncSession, *, workspace_id: int) -> list[Project]:
        """Lấy tất cả project thuộc một workspace."""
        stmt = select(Project).where(Project.workspace_id == workspace_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_in_workspace(
        self, db: AsyncSession, *, obj_in: ProjectCreate, workspace_id: int
    ) -> Project:
        """Tạo project trong một workspace cụ thể."""
        db_obj = Project(
            workspace_id=workspace_id,
            name=obj_in.name,
            description=obj_in.description,
            status="ACTIVE",
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_filtered(
        self,
        db: AsyncSession,
        *,
        workspace_id: int,
        status: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Project]:
        """Lọc project theo điều kiện, hỗ trợ tìm kiếm và phân trang."""
        stmt = select(Project).where(Project.workspace_id == workspace_id)
        if status:
            stmt = stmt.where(Project.status == status)
        if search:
            stmt = stmt.where(
                or_(
                    Project.name.ilike(f"%{search}%"),
                    Project.description.ilike(f"%{search}%"),
                )
            )
        stmt = stmt.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


project_repo = ProjectRepository(Project)
