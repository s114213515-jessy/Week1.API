import os
from typing import Annotated

from authlib.integrations.base_client import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import psycopg
from jwt.exceptions import InvalidTokenError
from starlette.responses import RedirectResponse

from app.core.database import connection_dependency
from app.core.security import (
    access_token_lifetime,
    create_access_token,
    decode_access_token,
)
from app.repositories.members import (
    MemberRecord,
    get_active_member,
    upsert_google_member,
)
from app.schemas.member import MemberProfile

router = APIRouter(tags=["authentication"])
DatabaseConnection = Annotated[psycopg.Connection, Depends(connection_dependency)]
bearer_scheme = HTTPBearer(auto_error=False)
ACCESS_TOKEN_COOKIE = "access_token"
GOOGLE_METADATA_URL = "https://accounts.google.com/.well-known/openid-configuration"


def _required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication is not configured: {name}",
        )
    return value


def _google_client(request: Request):
    if "session" not in request.scope:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication session is not configured",
        )
    oauth = OAuth()
    return oauth.register(
        name="google",
        client_id=_required_setting("GOOGLE_CLIENT_ID"),
        client_secret=_required_setting("GOOGLE_CLIENT_SECRET"),
        server_metadata_url=GOOGLE_METADATA_URL,
        client_kwargs={"scope": "openid email profile"},
    )


def _cookie_secure() -> bool:
    value = os.getenv("AUTH_COOKIE_SECURE", "true").lower()
    if value not in {"true", "false"}:
        raise RuntimeError("AUTH_COOKIE_SECURE must be true or false")
    return value == "true"


def _profile(member: MemberRecord) -> MemberProfile:
    return MemberProfile(
        name=member["name"],
        email=member["email"],
        picture=member["picture"],
    )


def get_authenticated_member_id(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> int:
    token = (
        credentials.credentials
        if credentials is not None
        else request.cookies.get(ACCESS_TOKEN_COOKIE)
    )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        member_id = decode_access_token(token)
    except InvalidTokenError:
        member_id = None
    if member_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return member_id


AuthenticatedMemberId = Annotated[int, Depends(get_authenticated_member_id)]


def get_current_member(
    member_id: AuthenticatedMemberId,
    connection: DatabaseConnection,
) -> MemberRecord:
    member = get_active_member(connection, member_id)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Member is unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return member


CurrentMember = Annotated[MemberRecord, Depends(get_current_member)]


@router.get("/auth/google/login", include_in_schema=True)
async def google_login(request: Request) -> Response:
    client = _google_client(request)
    redirect_uri = _required_setting("GOOGLE_REDIRECT_URI")
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback", include_in_schema=True)
async def google_callback(
    request: Request,
    connection: DatabaseConnection,
) -> Response:
    client = _google_client(request)
    try:
        token = await client.authorize_access_token(request)
    except OAuthError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google sign-in was not completed",
        ) from error

    user_info = token.get("userinfo")
    if not isinstance(user_info, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google did not return a verified identity",
        )
    google_sub = user_info.get("sub")
    email = user_info.get("email")
    email_verified = user_info.get("email_verified") is True
    if (
        not isinstance(google_sub, str)
        or not google_sub
        or not isinstance(email, str)
        or not email
        or not email_verified
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A verified Google email is required",
        )

    name = user_info.get("name")
    picture = user_info.get("picture")
    member = upsert_google_member(
        connection,
        google_sub=google_sub,
        email=email,
        name=name if isinstance(name, str) else None,
        picture=picture if isinstance(picture, str) else None,
    )
    if not member["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This member account is disabled",
        )

    request.session.clear()
    response = RedirectResponse(
        os.getenv("AUTH_SUCCESS_REDIRECT_URL", "/"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=create_access_token(member["id"]),
        max_age=access_token_lifetime(),
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        path="/",
    )
    return response


@router.get("/auth/me", response_model=MemberProfile)
def read_current_member(member: CurrentMember) -> MemberProfile:
    return _profile(member)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        path="/",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
