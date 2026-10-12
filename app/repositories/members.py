from typing import TypedDict

from psycopg import Connection
from psycopg.rows import dict_row


class MemberRecord(TypedDict):
    id: int
    google_sub: str
    email: str
    name: str | None
    picture: str | None
    is_active: bool


def upsert_google_member(
    connection: Connection,
    *,
    google_sub: str,
    email: str,
    name: str | None,
    picture: str | None,
) -> MemberRecord:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            INSERT INTO public.members (google_sub, email, name, picture)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (google_sub) DO UPDATE
            SET email = EXCLUDED.email,
                name = EXCLUDED.name,
                picture = EXCLUDED.picture,
                email_verified = TRUE,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id, google_sub, email, name, picture, is_active
            """,
            (google_sub, email, name, picture),
        )
        member = cursor.fetchone()
    if member is None:
        raise RuntimeError("Database did not return the authenticated member")
    connection.commit()
    return member


def get_active_member(
    connection: Connection,
    member_id: int,
) -> MemberRecord | None:
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT id, google_sub, email, name, picture, is_active
            FROM public.members
            WHERE id = %s AND is_active = TRUE AND email_verified = TRUE
            """,
            (member_id,),
        )
        return cursor.fetchone()
