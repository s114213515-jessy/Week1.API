from app.core.database import get_connection


def test_connection() -> None:
    with get_connection() as connection:
        print("連線成功:", connection.info.dbname)


if __name__ == "__main__":
    test_connection()
