import uuid

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import UUIDType, EmailType

from api.db import Base

class User(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(1024))
    email: Mapped[str] = mapped_column(EmailType, unique=True)
    password: Mapped[str] = mapped_column(String(1024))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
