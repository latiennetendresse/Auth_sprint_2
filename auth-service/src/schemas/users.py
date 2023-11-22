from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from schemas.base import OrjsonBaseModel


class UserBase(OrjsonBaseModel):
    email: EmailStr
    name: str = Field(title="Имя")


class UserCreate(UserBase):
    password: str = Field(title="Пароль")


class UserPatch(OrjsonBaseModel):
    email: Optional[EmailStr]
    name: Optional[str] = Field(title="Имя")
    password: Optional[str] = Field(title="Пароль")


class UserResponse(UserBase):
    id: UUID

    class Config:
        orm_mode = True
