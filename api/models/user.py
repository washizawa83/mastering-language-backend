import uuid
from typing import List

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import UUIDType, EmailType

from api.db import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(1024))
    email: Mapped[str] = mapped_column(EmailType, unique=True)
    password: Mapped[str] = mapped_column(String(1024))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    decks: Mapped[List['Deck']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )
