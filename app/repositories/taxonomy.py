from typing import TypedDict

from psycopg import Connection
from psycopg.rows import dict_row

from app.schemas.taxonomy import CategoryCreate, TagCreate


class CategoryRecord(TypedDict):
    id: int
    name: str


class TagRecord(TypedDict):
    id: int
    name: str
    note_count: int


def list_category_records(connection: Connection) -> list[CategoryRecord]:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute("SELECT id, name FROM categories ORDER BY name")
        return cursor.fetchall()


def create_category_record(
    connection: Connection,
    category_data: CategoryCreate,
) -> CategoryRecord:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "INSERT INTO categories (name) VALUES (%s) RETURNING id, name",
            (category_data.name,),
        )
        category = cursor.fetchone()
    if category is None:
        raise RuntimeError("Database did not return the created category")
    connection.commit()
    return category


def list_tag_records(connection: Connection) -> list[TagRecord]:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT t.id, t.name, COUNT(nt.note_id)::int AS note_count
            FROM tags AS t
            LEFT JOIN note_tags AS nt ON nt.tag_id = t.id
            GROUP BY t.id
            ORDER BY t.name
            """
        )
        return cursor.fetchall()


def create_tag_record(
    connection: Connection,
    tag_data: TagCreate,
) -> TagRecord:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            "INSERT INTO tags (name) VALUES (%s) RETURNING id, name",
            (tag_data.name,),
        )
        tag = cursor.fetchone()
    if tag is None:
        raise RuntimeError("Database did not return the created tag")
    connection.commit()
    return {**tag, "note_count": 0}
