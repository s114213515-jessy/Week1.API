from datetime import datetime
from typing import TypedDict

from psycopg import Connection
from psycopg.rows import dict_row

from app.schemas.note import NoteCreate


class CategoryRecord(TypedDict):
    id: int
    name: str


class TagRecord(TypedDict):
    id: int
    name: str


class NoteRecord(TypedDict):
    id: int
    title: str
    content: str | None
    created_at: datetime
    category: CategoryRecord | None
    tags: list[TagRecord]


NOTE_SELECT = """
    SELECT
        n.id,
        n.title,
        n.content,
        n.created_at,
        CASE
            WHEN c.id IS NULL THEN NULL
            ELSE jsonb_build_object('id', c.id, 'name', c.name)
        END AS category,
        COALESCE(
            jsonb_agg(
                jsonb_build_object('id', t.id, 'name', t.name)
                ORDER BY t.name
            ) FILTER (WHERE t.id IS NOT NULL),
            '[]'::jsonb
        ) AS tags
    FROM notes AS n
    LEFT JOIN categories AS c ON c.id = n.category_id
    LEFT JOIN note_tags AS nt ON nt.note_id = n.id
    LEFT JOIN tags AS t ON t.id = nt.tag_id
"""


def _get_note_records(
    connection: Connection,
    where_clause: str = "",
    parameters: tuple[object, ...] = (),
) -> list[NoteRecord]:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            f"""
            {NOTE_SELECT}
            {where_clause}
            GROUP BY n.id, c.id
            ORDER BY n.id
            """,
            parameters,
        )
        return cursor.fetchall()


def list_note_records(
    connection: Connection,
    category_id: int | None = None,
    tag_id: int | None = None,
) -> list[NoteRecord]:
    filters: list[str] = []
    parameters: list[int] = []
    if category_id is not None:
        filters.append("n.category_id = %s")
        parameters.append(category_id)
    if tag_id is not None:
        filters.append(
            "EXISTS (SELECT 1 FROM note_tags AS filter_nt "
            "WHERE filter_nt.note_id = n.id AND filter_nt.tag_id = %s)"
        )
        parameters.append(tag_id)
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    return _get_note_records(connection, where_clause, tuple(parameters))


def get_note_record(connection: Connection, note_id: int) -> NoteRecord | None:
    notes = _get_note_records(connection, "WHERE n.id = %s", (note_id,))
    return notes[0] if notes else None


def _validate_relations(
    connection: Connection,
    category_id: int | None,
    tag_ids: list[int],
) -> None:
    with connection.cursor() as cursor:
        if category_id is not None:
            cursor.execute("SELECT 1 FROM categories WHERE id = %s", (category_id,))
            if cursor.fetchone() is None:
                raise RelatedRecordNotFound("Category not found")
        if tag_ids:
            cursor.execute("SELECT id FROM tags WHERE id = ANY(%s)", (tag_ids,))
            found_tag_ids = {row[0] for row in cursor.fetchall()}
            if found_tag_ids != set(tag_ids):
                raise RelatedRecordNotFound("One or more tags were not found")


def _replace_note_tags(
    connection: Connection,
    note_id: int,
    tag_ids: list[int],
) -> None:
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM note_tags WHERE note_id = %s", (note_id,))
        if tag_ids:
            cursor.executemany(
                "INSERT INTO note_tags (note_id, tag_id) VALUES (%s, %s)",
                [(note_id, tag_id) for tag_id in tag_ids],
            )


class RelatedRecordNotFound(Exception):
    pass


def create_note_record(
    connection: Connection,
    note_data: NoteCreate,
) -> NoteRecord:
    _validate_relations(connection, note_data.category_id, note_data.tag_ids)
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            INSERT INTO notes (title, content, category_id)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (note_data.title, note_data.content, note_data.category_id),
        )
        row = cursor.fetchone()
    if row is None:
        raise RuntimeError("Database did not return the created note id")
    _replace_note_tags(connection, row["id"], note_data.tag_ids)
    note = get_note_record(connection, row["id"])
    if note is None:
        raise RuntimeError("Database did not return the created note")
    connection.commit()
    return note


def update_note_record(
    connection: Connection,
    note_id: int,
    note_data: NoteCreate,
) -> NoteRecord | None:
    _validate_relations(connection, note_data.category_id, note_data.tag_ids)
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            f"""
            UPDATE notes
            SET title = %s, content = %s, category_id = %s
            WHERE id = %s
            RETURNING id
            """,
            (
                note_data.title,
                note_data.content,
                note_data.category_id,
                note_id,
            ),
        )
        row = cursor.fetchone()
    if row is None:
        return None
    _replace_note_tags(connection, note_id, note_data.tag_ids)
    note = get_note_record(connection, note_id)
    if note is None:
        raise RuntimeError("Database did not return the updated note")
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
