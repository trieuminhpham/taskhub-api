from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.routers import auth, tasks, users


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting {settings.app_name}...")
    yield
    # Shutdown
    print(f"👋 Shutting down {settings.app_name}...")


app = FastAPI(
    title=settings.app_name,
    description="TaskHub — Task Management API",
    version="0.1.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)

@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "app": settings.app_name}
