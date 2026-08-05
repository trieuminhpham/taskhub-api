from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_workspace_member
from app.models.domain import User, WorkspaceMember
from app.repositories.comment import comment_repo
from app.repositories.task import task_repo
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate

router = APIRouter(
    prefix="/api/v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/comments",
    tags=["Comments"],
)


@router.get("/", response_model=list[CommentResponse])
async def list_comments(
    workspace_id: int,
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    member: WorkspaceMember = Depends(get_workspace_member),
) -> list[CommentResponse]:
    """Lấy tất cả bình luận của một task."""
    return await comment_repo.get_by_task(db, task_id=task_id)


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    workspace_id: int,
    project_id: int,
    task_id: int,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
) -> CommentResponse:
    """Tạo bình luận mới. Mọi thành viên đều được phép bình luận."""
    # Kiểm tra task tồn tại
    task = await task_repo.get(db, id=task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return await comment_repo.create_for_task(
        db, obj_in=comment_in, task_id=task_id, author_id=current_user.id
    )


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    workspace_id: int,
    project_id: int,
    task_id: int,
    comment_id: int,
    comment_in: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
) -> CommentResponse:
    """Sửa bình luận. Chỉ tác giả của bình luận mới được sửa."""
    comment = await comment_repo.get(db, id=comment_id)
    if not comment or comment.task_id != task_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    # Chỉ tác giả mới được sửa
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments",
        )

    return await comment_repo.update(db, db_obj=comment, obj_in=comment_in)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    workspace_id: int,
    project_id: int,
    task_id: int,
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: WorkspaceMember = Depends(get_workspace_member),
) -> None:
    """Xóa bình luận. Chỉ tác giả mới được xóa."""
    comment = await comment_repo.get(db, id=comment_id)
    if not comment or comment.task_id != task_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
        )

    await comment_repo.delete(db, id=comment_id)
