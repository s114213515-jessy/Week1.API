from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

ClassName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]


class ClassCreate(BaseModel):
    parent_id: int = Field(ge=0)
    parent_name: ClassName
    name: ClassName


class SubclassResponse(BaseModel):
    pcid: int
    parent_name: str
    cid: int
    child_name: str


class ClassResponse(BaseModel):
    cid: int
    name: str
    idpath: str | None
    namepath: str | None
