from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.schemas.taxonomy import CategoryResponse, TagResponse

NoteTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]
NoteTagIds = Annotated[int, Field(gt=0)]


class NoteCreate(BaseModel):
    title: NoteTitle
    content: str | None = None
    category_id: int | None = Field(default=None, gt=0)
    tag_ids: list[NoteTagIds] = Field(default_factory=list, max_length=50)

    @field_validator("tag_ids")
    @classmethod
    def tag_ids_must_be_unique(cls, tag_ids: list[int]) -> list[int]:
        if len(tag_ids) != len(set(tag_ids)):
            raise ValueError("tag_ids must not contain duplicates")
        return tag_ids


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str | None
    created_at: datetime
    category: CategoryResponse | None = None
    tags: list[TagResponse] = Field(default_factory=list)
