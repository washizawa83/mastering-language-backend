import uuid
from typing import List

from sqlalchemy import String, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import UUIDType, EmailType

from api.db import Base


ONE_DAY = 86400
THREE_DAYS = 259200
ONE_WEEK = 604800
TWO_WEEKS = 1209600
ONE_MONTH = 2592000
THREE_MONTHS = 7776000
SIX_MONTHS = 15552000


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(1024))
    email: Mapped[str] = mapped_column(EmailType, unique=True)
    password: Mapped[str] = mapped_column(String(1024))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    decks: Mapped[List['Deck']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )

    cards: Mapped[List['Card']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )

    user_settings: Mapped['UserSettings'] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )


class UserSettings(Base):
    __tablename__ = 'user_settings'

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4
    )
    level_one: Mapped[int] = mapped_column(Integer, default=ONE_DAY)
    level_two: Mapped[int] = mapped_column(Integer, default=THREE_DAYS)
    level_three: Mapped[int] = mapped_column(Integer, default=ONE_WEEK)
    level_four: Mapped[int] = mapped_column(Integer, default=TWO_WEEKS)
    level_five: Mapped[int] = mapped_column(Integer, default=ONE_MONTH)
    level_six: Mapped[int] = mapped_column(Integer, default=THREE_MONTHS)
    level_seven: Mapped[int] = mapped_column(Integer, default=SIX_MONTHS)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(
        back_populates='user_settings', single_parent=True
    )

    __table_args__ = (UniqueConstraint('user_id'),)
