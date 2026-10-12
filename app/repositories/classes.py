from typing import TypedDict

from psycopg import Connection
from psycopg.rows import dict_row

from app.schemas.classes import ClassCreate


class SubclassRecord(TypedDict):
    pcid: int
    parent_name: str
    cid: int
    child_name: str


class ClassRecord(TypedDict):
    cid: int
    name: str
    idpath: str | None
    namepath: str | None


def list_subclass_records(
    connection: Connection,
    parent_id: int,
) -> list[SubclassRecord]:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT pcid, parent_name, cid, child_name
            FROM public.vd_subclass
            WHERE pcid = %s
            ORDER BY cid
            """,
            (parent_id,),
        )
        return cursor.fetchall()


def create_class_record(
    connection: Connection,
    class_data: ClassCreate,
) -> ClassRecord:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT public.insertclass(%s, %s, %s) AS cid
            """,
            (class_data.parent_id, class_data.parent_name, class_data.name),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError("Database did not return the created class id")

        cursor.execute(
            """
            SELECT cid, name, idpath, namepath
            FROM public.class
            WHERE cid = %s
            """,
            (row["cid"],),
        )
        created_class = cursor.fetchone()
    if created_class is None:
        raise RuntimeError("Database did not return the created class")
    connection.commit()
    return created_class
