import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_ISSUER = "week1-api"


def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret or len(secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET_KEY must contain at least 32 bytes")
    return secret


def access_token_lifetime() -> int:
    try:
        lifetime = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "28800"))
    except ValueError as error:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_SECONDS must be an integer") from error
    if not 60 <= lifetime <= 86400:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_SECONDS must be between 60 and 86400")
    return lifetime


def create_access_token(member_id: int) -> str:
    now = datetime.now(timezone.utc)
    lifetime = access_token_lifetime()
    return jwt.encode(
        {
            "sub": str(member_id),
            "iss": JWT_ISSUER,
            "iat": now,
            "exp": now + timedelta(seconds=lifetime),
        },
        _jwt_secret(),
        algorithm="HS256",
    )


def decode_access_token(token: str) -> int | None:
    claims = jwt.decode(
        token,
        _jwt_secret(),
        algorithms=["HS256"],
        issuer=JWT_ISSUER,
        options={"require": ["exp", "iat", "iss", "sub"]},
    )
    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject.isdecimal():
        return None
    member_id = int(subject)
    return member_id if member_id > 0 else None
