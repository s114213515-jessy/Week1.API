from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

TaxonomyName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]


class CategoryCreate(BaseModel):
    name: TaxonomyName


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TagCreate(BaseModel):
    name: TaxonomyName


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    note_count: int = 0
