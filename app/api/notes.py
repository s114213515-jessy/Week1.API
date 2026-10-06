from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
import psycopg

from app.core.database import connection_dependency
from app.repositories.notes import (
    RelatedRecordNotFound,
    create_note_record,
    delete_note_record,
    get_note_record,
    list_note_records,
    update_note_record,
)
from app.schemas.note import NoteCreate, NoteResponse

router = APIRouter(tags=["notes"])
DatabaseConnection = Annotated[psycopg.Connection, Depends(connection_dependency)]


@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: NoteCreate,
    connection: DatabaseConnection,
) -> NoteResponse:
    try:
        return create_note_record(connection, note_data)
    except RelatedRecordNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/notes", response_model=list[NoteResponse])
def list_notes(
    connection: DatabaseConnection,
    category_id: int | None = Query(default=None, gt=0),
    tag_id: int | None = Query(default=None, gt=0),
) -> list[NoteResponse]:
    return list_note_records(connection, category_id=category_id, tag_id=tag_id)


@router.get("/notes/{note_id}", response_model=NoteResponse)
@router.get(
    "/note/{note_id}",
    response_model=NoteResponse,
    include_in_schema=False,
)
def get_note(note_id: int, connection: DatabaseConnection) -> NoteResponse:
    note = get_note_record(connection, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_data: NoteCreate,
    connection: DatabaseConnection,
) -> NoteResponse:
    try:
        note = update_note_record(connection, note_id, note_data)
    except RelatedRecordNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_note(note_id: int, connection: DatabaseConnection) -> Response:
    deleted = delete_note_record(connection, note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
