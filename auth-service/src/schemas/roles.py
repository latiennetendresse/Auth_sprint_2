from uuid import UUID

from pydantic import Field

from schemas.base import OrjsonBaseModel


class RoleBase(OrjsonBaseModel):
    name: str = Field(title="Название")


class RoleResponse(RoleBase):
    id: UUID

    class Config:
        orm_mode = True
