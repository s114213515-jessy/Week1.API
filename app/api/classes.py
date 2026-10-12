from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
import psycopg

from app.api.auth import get_current_member
from app.core.database import connection_dependency
from app.repositories.classes import create_class_record, list_subclass_records
from app.schemas.classes import ClassCreate, ClassResponse, SubclassResponse

router = APIRouter(
    tags=["academic classes"],
    dependencies=[Depends(get_current_member)],
)
DatabaseConnection = Annotated[psycopg.Connection, Depends(connection_dependency)]


@router.get(
    "/subclass/pcid/{parent_id}",
    response_model=list[SubclassResponse],
)
def list_subclasses(
    parent_id: Annotated[int, Path(ge=0)],
    connection: DatabaseConnection,
) -> list[SubclassResponse]:
    return list_subclass_records(connection, parent_id)


@router.post(
    "/classes",
    response_model=ClassResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_class(
    class_data: ClassCreate,
    connection: DatabaseConnection,
) -> ClassResponse:
    try:
        return create_class_record(connection, class_data)
    except psycopg.errors.ForeignKeyViolation as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent class not found",
        ) from error
    except psycopg.errors.CheckViolation as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Parent name does not match the parent id, or class name is empty",
        ) from error
    except psycopg.errors.UniqueViolation as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The class path conflicts with an existing class",
        ) from error
