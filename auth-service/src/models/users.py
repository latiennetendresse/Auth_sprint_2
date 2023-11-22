from pydantic import EmailStr
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base
from models.mixins import IdMixin, TimestampMixin
from models.roles import UserRole  # noqa: F401


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))

    roles = relationship("UserRole", back_populates="user", lazy="selectin")

    def __init__(self, email: EmailStr, password: str, name: str) -> None:
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.name = name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
