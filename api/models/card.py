import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import UUIDType
from sqlalchemy.sql import func

from api.db import Base


class Card(Base):
    __tablename__ = 'cards'

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(binary=False), primary_key=True, default=uuid.uuid4
    )
    sentence: Mapped[str] = mapped_column(String(1024))
    meaning: Mapped[str] = mapped_column(String(1024))
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    etymology: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    previous_answer_date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, nullable=True
    )
    next_answer_date: Mapped[datetime | None] = mapped_column(
        TIMESTAMP, nullable=True
    )
    retention_state: Mapped[bool] = mapped_column(Boolean, default=False)
    savings_score: Mapped[int] = mapped_column(Integer, default=0)

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )

    deck_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('decks.id'))
    deck: Mapped['Deck'] = relationship(back_populates='cards')

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='cards')
