from datetime import datetime
from typing import TypedDict

from psycopg import Connection
from psycopg.rows import dict_row

from app.schemas.note import NoteCreate


class NoteRecord(TypedDict):
    id: int
    title: str
    content: str | None
    created_at: datetime


NOTE_COLUMNS = "id, title, content, created_at"


def list_note_records(connection: Connection) -> list[NoteRecord]:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(f"SELECT {NOTE_COLUMNS} FROM notes ORDER BY id")
        return cursor.fetchall()


def get_note_record(connection: Connection, note_id: int) -> NoteRecord | None:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            f"SELECT {NOTE_COLUMNS} FROM notes WHERE id = %s",
            (note_id,),
        )
        return cursor.fetchone()


def create_note_record(
    connection: Connection,
    note_data: NoteCreate,
) -> NoteRecord:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            f"""
            INSERT INTO notes (title, content)
            VALUES (%s, %s)
            RETURNING {NOTE_COLUMNS}
            """,
            (note_data.title, note_data.content),
        )
        note = cursor.fetchone()
    if note is None:
        raise RuntimeError("Database did not return the created note")
    connection.commit()
    return note


def update_note_record(
    connection: Connection,
    note_id: int,
    note_data: NoteCreate,
) -> NoteRecord | None:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            f"""
            UPDATE notes
            SET title = %s, content = %s
            WHERE id = %s
            RETURNING {NOTE_COLUMNS}
            """,
            (note_data.title, note_data.content, note_id),
        )
        note = cursor.fetchone()
    if note is not None:
        connection.commit()
    return note


def delete_note_record(connection: Connection, note_id: int) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM notes WHERE id = %s RETURNING id",
            (note_id,),
        )
        deleted = cursor.fetchone() is not None
    if deleted:
        connection.commit()
    return deleted
