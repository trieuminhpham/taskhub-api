from pydantic import BaseModel, ConfigDict, Field


class LabelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Bug"])
    color: str = Field(..., min_length=1, max_length=50, examples=["#FF0000"])


class LabelUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    color: str | None = Field(None, min_length=1, max_length=50)


class LabelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    color: str
