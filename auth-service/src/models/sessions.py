from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base
from models.mixins import IdMixin, TimestampMixin


class Session(IdMixin, TimestampMixin, Base):
    __tablename__ = "sessions"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user_agent = Column(Text)
    access_jti = Column(UUID(as_uuid=True))
    refresh_jti = Column(UUID(as_uuid=True))
    session_exp = Column(DateTime)
