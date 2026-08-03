from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_workspace_member, require_editor, require_owner
from app.models.domain import User, WorkspaceMember
from app.repositories.workspace import member_repo, workspace_repo
from app.schemas.workspace import (
    MemberInvite,
    MemberResponse,
    MemberUpdate,
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
)

router = APIRouter(prefix="/api/v1/workspaces", tags=["Workspaces"])


# ────────────────────────────────────────────────
# WORKSPACE CRUD
# ────────────────────────────────────────────────

@router.get("/", response_model=list[WorkspaceResponse])
async def list_my_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WorkspaceResponse]:
    """Lấy danh sách workspace mà user đang là thành viên."""
    return await workspace_repo.get_user_workspaces(db, user_id=current_user.id)


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_in: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkspaceResponse:
    """Tạo workspace mới. User tạo sẽ tự động là OWNER."""
    return await workspace_repo.create_with_owner(db, obj_in=workspace_in, owner_id=current_user.id)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(get_workspace_member),  # Chỉ thành viên mới xem được
) -> WorkspaceResponse:
    """Lấy chi tiết một workspace."""
    workspace = await workspace_repo.get(db, id=workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: int,
    workspace_in: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_editor),  # Cần ít nhất EDITOR
) -> WorkspaceResponse:
    """Cập nhật tên workspace. Yêu cầu quyền EDITOR hoặc OWNER."""
    workspace = await workspace_repo.get(db, id=workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return await workspace_repo.update(db, db_obj=workspace, obj_in=workspace_in)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_owner),  # Chỉ OWNER mới xóa được
) -> None:
    """Xóa workspace. Yêu cầu quyền OWNER."""
    workspace = await workspace_repo.delete(db, id=workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")


# ────────────────────────────────────────────────
# MEMBER MANAGEMENT
# ────────────────────────────────────────────────

@router.get("/{workspace_id}/members", response_model=list[MemberResponse])
async def list_members(
    workspace_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(get_workspace_member),  # Thành viên mới xem được
) -> list[MemberResponse]:
    """Lấy danh sách thành viên trong workspace."""
    return await member_repo.get_all_members(db, workspace_id=workspace_id)


@router.post("/{workspace_id}/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    workspace_id: int,
    member_in: MemberInvite,
    db: AsyncSession = Depends(get_db),
    owner: WorkspaceMember = Depends(require_owner),  # Chỉ OWNER mới mời được
) -> MemberResponse:
    """Mời thành viên mới vào workspace. Yêu cầu quyền OWNER."""
    # Kiểm tra user đã là thành viên chưa
    existing = await member_repo.get_member(db, workspace_id=workspace_id, user_id=member_in.user_id)
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this workspace")

    return await member_repo.add_member(
        db, workspace_id=workspace_id, user_id=member_in.user_id, role=member_in.role
    )


@router.patch("/{workspace_id}/members/{user_id}", response_model=MemberResponse)
async def update_member_role(
    workspace_id: int,
    user_id: int,
    member_in: MemberUpdate,
    db: AsyncSession = Depends(get_db),
    owner: WorkspaceMember = Depends(require_owner),  # Chỉ OWNER mới đổi quyền được
) -> MemberResponse:
    """Thay đổi quyền của một thành viên. Yêu cầu quyền OWNER."""
    member = await member_repo.get_member(db, workspace_id=workspace_id, user_id=user_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return await member_repo.update_member_role(db, member=member, role=member_in.role)


@router.delete("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    workspace_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    owner: WorkspaceMember = Depends(require_owner),  # Chỉ OWNER mới đuổi được
) -> None:
    """Đuổi thành viên khỏi workspace. Yêu cầu quyền OWNER."""
    removed = await member_repo.remove_member(db, workspace_id=workspace_id, user_id=user_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Member not found")
