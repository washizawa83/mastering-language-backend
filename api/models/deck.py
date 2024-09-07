import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import UUIDType
from sqlalchemy.sql import func

from api.db import Base


class Deck(Base):
    __tablename__ = 'decks'

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(1024))
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='decks')

    cards: Mapped[List['Card']] = relationship(
        back_populates='deck', cascade='all, delete-orphan'
    )
