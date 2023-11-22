from datetime import datetime
from typing import Optional
from uuid import UUID

from schemas.base import OrjsonBaseModel


class SessionResponse(OrjsonBaseModel):
    id: UUID
    user_agent: str
    created_at: datetime
    modified_at: Optional[datetime]
    session_exp: Optional[datetime]

    class Config:
        orm_mode = True
