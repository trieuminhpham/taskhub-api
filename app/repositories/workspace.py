from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Workspace, WorkspaceMember
from app.repositories.base import BaseRepository
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class WorkspaceRepository(BaseRepository[Workspace, WorkspaceCreate, WorkspaceUpdate]):

    async def create_with_owner(self, db: AsyncSession, *, obj_in: WorkspaceCreate, owner_id: int) -> Workspace:
        """Tạo workspace và tự động thêm owner vào bảng workspace_members."""
        # 1. Tạo workspace
        db_workspace = Workspace(name=obj_in.name, owner_id=owner_id)
        db.add(db_workspace)
        await db.flush()  # flush để lấy id của workspace vừa tạo

        # 2. Thêm owner vào bảng workspace_members với role OWNER
        db_member = WorkspaceMember(
            workspace_id=db_workspace.id,
            user_id=owner_id,
            role="OWNER",
        )
        db.add(db_member)
        await db.commit()
        await db.refresh(db_workspace)
        return db_workspace

    async def get_user_workspaces(self, db: AsyncSession, *, user_id: int) -> list[Workspace]:
        """Lấy tất cả workspace mà user đang là thành viên."""
        stmt = (
            select(Workspace)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(WorkspaceMember.user_id == user_id)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


class WorkspaceMemberRepository:

    async def get_member(
        self, db: AsyncSession, *, workspace_id: int, user_id: int
    ) -> WorkspaceMember | None:
        stmt = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_all_members(self, db: AsyncSession, *, workspace_id: int) -> list[WorkspaceMember]:
        stmt = select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def add_member(
        self, db: AsyncSession, *, workspace_id: int, user_id: int, role: str = "VIEWER"
    ) -> WorkspaceMember:
        db_member = WorkspaceMember(workspace_id=workspace_id, user_id=user_id, role=role)
        db.add(db_member)
        await db.commit()
        await db.refresh(db_member)
        return db_member

    async def update_member_role(
        self, db: AsyncSession, *, member: WorkspaceMember, role: str
    ) -> WorkspaceMember:
        member.role = role
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member

    async def remove_member(
        self, db: AsyncSession, *, workspace_id: int, user_id: int
    ) -> bool:
        member = await self.get_member(db, workspace_id=workspace_id, user_id=user_id)
        if not member:
            return False
        await db.delete(member)
        await db.commit()
        return True


workspace_repo = WorkspaceRepository(Workspace)
member_repo = WorkspaceMemberRepository()
