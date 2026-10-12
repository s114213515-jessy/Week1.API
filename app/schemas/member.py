from pydantic import BaseModel


class MemberProfile(BaseModel):
    name: str | None
    email: str
    picture: str | None
