from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Khởi tạo Async Engine kết nối MySQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Tạo Session factory để dùng cho từng request
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Dependency để nhúng vào API endpoints
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Cung cấp Database Session cho mỗi request và tự đóng khi xong."""
    async with AsyncSessionLocal() as session:
        yield session
