from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.domain import User, WorkspaceMember
from app.repositories.user import user_repo
from app.repositories.workspace import member_repo
from app.schemas.auth import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception

        token_data = TokenPayload(sub=int(user_id), type=token_type)
    except JWTError as e:
        raise credentials_exception from e

    user = await user_repo.get(db, id=token_data.sub)
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def get_workspace_member(
    workspace_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkspaceMember:
    """Kiểm tra user có phải thành viên của workspace không."""
    member = await member_repo.get_member(db, workspace_id=workspace_id, user_id=current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )
    return member


async def require_editor(
    member: WorkspaceMember = Depends(get_workspace_member),
) -> WorkspaceMember:
    """Yêu cầu quyền EDITOR hoặc OWNER mới được thực hiện."""
    if member.role not in ("OWNER", "EDITOR"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need EDITOR or OWNER role to perform this action",
        )
    return member


async def require_owner(
    member: WorkspaceMember = Depends(get_workspace_member),
) -> WorkspaceMember:
    """Yêu cầu quyền OWNER mới được thực hiện."""
    if member.role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need OWNER role to perform this action",
        )
    return member
