from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_workspace_member, require_editor, require_owner
from app.models.domain import WorkspaceMember
from app.repositories.label import label_repo
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate

router = APIRouter(
    prefix="/api/v1/workspaces/{workspace_id}/projects/{project_id}/labels",
    tags=["Labels"],
)


@router.get("/", response_model=list[LabelResponse])
async def list_labels(
    workspace_id: int,
    project_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(get_workspace_member),
) -> list[LabelResponse]:
    """Lấy tất cả label trong project."""
    return await label_repo.get_by_project(db, project_id=project_id)


@router.post("/", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
async def create_label(
    workspace_id: int,
    project_id: int,
    label_in: LabelCreate,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_editor),
) -> LabelResponse:
    """Tạo label mới. Yêu cầu quyền EDITOR hoặc OWNER."""
    return await label_repo.create_for_project(db, obj_in=label_in, project_id=project_id)


@router.patch("/{label_id}", response_model=LabelResponse)
async def update_label(
    workspace_id: int,
    project_id: int,
    label_id: int,
    label_in: LabelUpdate,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_editor),
) -> LabelResponse:
    """Cập nhật label. Yêu cầu quyền EDITOR hoặc OWNER."""
    label = await label_repo.get(db, id=label_id)
    if not label or label.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
    return await label_repo.update(db, db_obj=label, obj_in=label_in)


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(
    workspace_id: int,
    project_id: int,
    label_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_owner),
) -> None:
    """Xóa label. Yêu cầu quyền OWNER."""
    label = await label_repo.get(db, id=label_id)
    if not label or label.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
    await label_repo.delete(db, id=label_id)


# ────────────────────────────────────────────────
# GẮN / GỠ LABEL KHỎI TASK
# ────────────────────────────────────────────────

@router.post("/tasks/{task_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_label_to_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    label_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_editor),
) -> None:
    """Gắn label vào task. Yêu cầu quyền EDITOR hoặc OWNER."""
    added = await label_repo.add_label_to_task(db, task_id=task_id, label_id=label_id)
    if not added:
        raise HTTPException(status_code=400, detail="Label already added to this task")


@router.delete("/tasks/{task_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_label_from_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    label_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_editor),
) -> None:
    """Gỡ label khỏi task. Yêu cầu quyền EDITOR hoặc OWNER."""
    removed = await label_repo.remove_label_from_task(db, task_id=task_id, label_id=label_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Label not found on this task")
