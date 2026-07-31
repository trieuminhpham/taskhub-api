from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.task import task_repo
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> list[TaskResponse]:
    """Get all tasks."""
    # Bây giờ sẽ lấy từ MySQL thông qua TaskRepository
    tasks = await task_repo.get_all(db, skip=skip, limit=limit)
    return tasks


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate, db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """Create a new task."""
    task = await task_repo.create(db, obj_in=task_in)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)) -> TaskResponse:
    """Get a task by ID."""
    task = await task_repo.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int, task_in: TaskUpdate, db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """Update a task (partial update)."""
    task = await task_repo.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task = await task_repo.update(db, db_obj=task, obj_in=task_in)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete a task."""
    task = await task_repo.delete(db, id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
