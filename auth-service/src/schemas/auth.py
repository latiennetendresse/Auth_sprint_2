from uuid import UUID

from pydantic import Field

from schemas.base import OrjsonBaseModel


class Credentials(OrjsonBaseModel):
    username: str = Field(title="Email")
    password: str = Field(title="Пароль")


class TokenPair(OrjsonBaseModel):
    access_token: str
    refresh_token: str


class LoginResponse(TokenPair):
    user_id: UUID
