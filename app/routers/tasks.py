from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

# In-memory store tạm thời (ngày 2 sẽ thay bằng database)
_fake_db: dict[int, dict] = {}
_next_id: int = 1


@router.get("/", response_model=list[TaskResponse])
async def list_tasks() -> list[dict]:
    """Get all tasks."""
    return list(_fake_db.values())


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_in: TaskCreate) -> dict:
    """Create a new task."""
    global _next_id  # noqa: PLW0603

    task = {
        "id": _next_id,
        **task_in.model_dump(),
        "created_at": datetime.now(),
    }
    _fake_db[_next_id] = task
    _next_id += 1

    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int) -> dict:
    """Get a task by ID."""
    task = _fake_db.get(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_in: TaskUpdate) -> dict:
    """Update a task (partial update)."""
    task = _fake_db.get(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    task.update(update_data)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int) -> None:
    """Delete a task."""
    if task_id not in _fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    del _fake_db[task_id]
