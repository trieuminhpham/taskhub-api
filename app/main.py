from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.routers import auth, comments, labels, projects, tasks, users, workspaces


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    print(f"🚀 Starting {settings.app_name}...")
    yield
    print(f"👋 Shutting down {settings.app_name}...")


app = FastAPI(
    title=settings.app_name,
    description="""
## 🚀 TaskHub — Task Management System

API quản lý công việc theo mô hình **Workspace → Project → Task**.

### Tính năng chính:
- 🔐 **Authentication** — JWT-based (Access Token + Refresh Token)
- 🏢 **Workspace** — Multi-tenant với phân quyền RBAC (OWNER / EDITOR / VIEWER)
- 📁 **Project** — Quản lý dự án trong Workspace, hỗ trợ filter và tìm kiếm
- ✅ **Task** — CRUD với assignee, due_date, priority, filter và phân trang
- 💬 **Comment** — Bình luận theo từng Task (author-based protection)
- 🏷️ **Label** — Nhãn màu sắc gắn vào Task
    """,
    version="1.0.0",
    contact={
        "name": "Trieu Minh Pham",
        "url": "https://github.com/trieuminhpham/taskhub-api",
    },
    lifespan=lifespan,
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Xử lý lỗi duplicate key hoặc vi phạm constraint từ database."""
    return JSONResponse(
        status_code=409,
        content={"detail": "Data conflict: the resource already exists or violates a constraint."},
    )


# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(workspaces.router)
app.include_router(projects.router)
app.include_router(comments.router)
app.include_router(labels.router)
app.include_router(tasks.router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "app": settings.app_name}
