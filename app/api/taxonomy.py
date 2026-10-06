from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
import psycopg

from app.core.database import connection_dependency
from app.repositories.taxonomy import (
    create_category_record,
    create_tag_record,
    list_category_records,
    list_tag_records,
)
from app.schemas.taxonomy import (
    CategoryCreate,
    CategoryResponse,
    TagCreate,
    TagResponse,
)

router = APIRouter(tags=["categories and tags"])
DatabaseConnection = Annotated[psycopg.Connection, Depends(connection_dependency)]


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(connection: DatabaseConnection) -> list[CategoryResponse]:
    return list_category_records(connection)


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category_data: CategoryCreate,
    connection: DatabaseConnection,
) -> CategoryResponse:
    try:
        return create_category_record(connection, category_data)
    except psycopg.errors.UniqueViolation as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists",
        ) from error


@router.get("/tags", response_model=list[TagResponse])
def list_tags(connection: DatabaseConnection) -> list[TagResponse]:
    return list_tag_records(connection)


@router.post(
    "/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tag(tag_data: TagCreate, connection: DatabaseConnection) -> TagResponse:
    try:
        return create_tag_record(connection, tag_data)
    except psycopg.errors.UniqueViolation as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A tag with this name already exists",
        ) from error
