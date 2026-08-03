from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# --- Workspace Schemas ---

class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Sun* Backend Team"])


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    owner_id: int
    created_at: datetime


# --- WorkspaceMember Schemas ---

class MemberRole(str):
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"


class MemberInvite(BaseModel):
    user_id: int
    role: str = Field(default="VIEWER", examples=["VIEWER", "EDITOR", "OWNER"])


class MemberUpdate(BaseModel):
    role: str = Field(..., examples=["VIEWER", "EDITOR", "OWNER"])


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workspace_id: int
    user_id: int
    role: str
