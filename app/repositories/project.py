from sqlalchemy import select
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


project_repo = ProjectRepository(Project)
