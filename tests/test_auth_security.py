import asyncio
import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import httpx
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.core.security import create_access_token, decode_access_token


class AccessTokenTests(unittest.TestCase):
    def test_signed_token_round_trips_member_id(self) -> None:
        with patch.dict(
            os.environ,
            {
                "JWT_SECRET_KEY": "x" * 48,
                "ACCESS_TOKEN_EXPIRE_SECONDS": "3600",
            },
        ):
            token = create_access_token(17)

            self.assertEqual(decode_access_token(token), 17)

    def test_tampered_token_is_rejected(self) -> None:
        with patch.dict(os.environ, {"JWT_SECRET_KEY": "x" * 48}):
            token = create_access_token(17)
            tampered = token[:-1] + ("a" if token[-1] != "a" else "b")

            with self.assertRaises(InvalidTokenError):
                decode_access_token(tampered)

    def test_expired_token_is_rejected(self) -> None:
        secret = "x" * 48
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {
                "sub": "17",
                "iss": "week1-api",
                "iat": now - timedelta(hours=2),
                "exp": now - timedelta(hours=1),
            },
            secret,
            algorithm="HS256",
        )

        with patch.dict(os.environ, {"JWT_SECRET_KEY": secret}):
            with self.assertRaises(ExpiredSignatureError):
                decode_access_token(token)

    def test_short_secret_is_rejected(self) -> None:
        with patch.dict(os.environ, {"JWT_SECRET_KEY": "too-short"}):
            with self.assertRaisesRegex(RuntimeError, "at least 32 bytes"):
                create_access_token(17)

    def test_protected_profile_rejects_missing_token_before_database_access(self) -> None:
        from app.main import app

        async def get_unauthenticated_responses() -> list[httpx.Response]:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as client:
                return [
                    await client.get(path)
                    for path in (
                        "/api/auth/me",
                        "/api/notes",
                        "/api/subclass/pcid/0",
                    )
                ]

        with patch(
            "app.core.database.get_connection",
            side_effect=AssertionError("Unauthenticated request must not connect to DB"),
        ):
            responses = asyncio.run(get_unauthenticated_responses())

        self.assertEqual([response.status_code for response in responses], [401, 401, 401])

    def test_openapi_contains_auth_routes(self) -> None:
        from app.main import app

        paths = app.openapi()["paths"]

        self.assertIn("/api/auth/google/login", paths)
        self.assertIn("/api/auth/google/callback", paths)
        self.assertIn("/api/auth/me", paths)
        self.assertIn("/api/auth/logout", paths)


if __name__ == "__main__":
    unittest.main()
