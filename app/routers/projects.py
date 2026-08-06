from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_workspace_member, require_editor, require_owner
from app.models.domain import WorkspaceMember
from app.repositories.project import project_repo
from app.repositories.task import task_repo
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/api/v1/workspaces/{workspace_id}/projects", tags=["Projects"])


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    workspace_id: int,
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(get_workspace_member),
) -> list[ProjectResponse]:
    """Lấy danh sách project. Hỗ trợ filter theo status, tìm kiếm theo tên và phân trang."""
    return await project_repo.get_filtered(
        db,
        workspace_id=workspace_id,
        status=status,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    workspace_id: int,
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_editor),
) -> ProjectResponse:
    """Tạo project mới. Yêu cầu quyền EDITOR hoặc OWNER."""
    return await project_repo.create_in_workspace(
        db, obj_in=project_in, workspace_id=workspace_id
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    workspace_id: int,
    project_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(get_workspace_member),
) -> ProjectResponse:
    """Lấy chi tiết một project."""
    project = await project_repo.get(db, id=project_id)
    if not project or project.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    workspace_id: int,
    project_id: int,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_editor),
) -> ProjectResponse:
    """Cập nhật project. Yêu cầu quyền EDITOR hoặc OWNER."""
    project = await project_repo.get(db, id=project_id)
    if not project or project.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return await project_repo.update(db, db_obj=project, obj_in=project_in)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    workspace_id: int,
    project_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_owner),
) -> None:
    """Xóa project. Yêu cầu quyền OWNER."""
    project = await project_repo.get(db, id=project_id)
    if not project or project.workspace_id != workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    await project_repo.delete(db, id=project_id)


# ────────────────────────────────────────────────
# TASK CRUD (lồng trong Project)
# ────────────────────────────────────────────────

@router.get("/{project_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    workspace_id: int,
    project_id: int,
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    assignee_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(get_workspace_member),
) -> list[TaskResponse]:
    """Lấy danh sách task. Hỗ trợ filter theo status, priority, assignee, tìm kiếm và phân trang."""
    return await task_repo.get_filtered(
        db,
        project_id=project_id,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    workspace_id: int,
    project_id: int,
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_editor),
) -> TaskResponse:
    """Tạo task trong project. Yêu cầu quyền EDITOR hoặc OWNER."""
    return await task_repo.create_in_project(
        db, obj_in=task_in, project_id=project_id, created_by=member.user_id
    )


@router.get("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(get_workspace_member),
) -> TaskResponse:
    """Lấy chi tiết một task."""
    task = await task_repo.get(db, id=task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_editor),
) -> TaskResponse:
    """Cập nhật task. Yêu cầu quyền EDITOR hoặc OWNER."""
    task = await task_repo.get(db, id=task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return await task_repo.update(db, db_obj=task, obj_in=task_in)


@router.delete("/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    workspace_id: int,
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(require_editor),
) -> None:
    """Xóa task. Yêu cầu quyền EDITOR hoặc OWNER."""
    task = await task_repo.get(db, id=task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await task_repo.delete(db, id=task_id)
