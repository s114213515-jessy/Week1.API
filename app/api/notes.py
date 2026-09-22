from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
import psycopg

from app.core.database import connection_dependency

router = APIRouter(tags=["notes"])


@router.get("/note/{note_id}")
def get_note(
    note_id: int,
    connection: Annotated[psycopg.Connection, Depends(connection_dependency)],
) -> dict[str, object]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, title, content, created_at
            FROM notes
            WHERE id = %s
            """,
            (note_id,),
        )
        note = cursor.fetchone()

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    return {
        "id": note[0],
        "title": note[1],
        "content": note[2],
        "created_at": note[3],
    }
