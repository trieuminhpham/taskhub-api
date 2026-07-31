from app.models.domain import Task
from app.repositories.base import BaseRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
    pass

# Khởi tạo instance duy nhất để dùng trong Routers
task_repo = TaskRepository(Task)
