from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import get_password_hash, verify_password
from app.models.domain import User
from app.repositories.user import user_repo
from app.schemas.user import PasswordUpdate, UserResponse, UserUpdate

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Lấy thông tin profile của user đang đăng nhập."""
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_profile(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Cập nhật thông tin profile."""
    user = await user_repo.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.post("/me/password")
async def change_password(
    password_in: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Thay đổi mật khẩu."""
    if not verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    current_user.hashed_password = get_password_hash(password_in.new_password)
    db.add(current_user)
    await db.commit()

    return {"message": "Password updated successfully"}
