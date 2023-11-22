from sqlalchemy import Column, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base
from models.mixins import IdMixin, TimestampMixin


class SocialAccount(IdMixin, TimestampMixin, Base):
    __tablename__ = "social_account"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    social_id = Column(Text, nullable=False)
    social_name = Column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("social_id", "social_name", name="social_pk"),)

    def __repr__(self):
        return f"<SocialAccount {self.social_name}:{self.user_id}>"
