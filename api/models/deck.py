import uuid

from sqlalchemy import String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import UUIDType, EmailType
from sqlalchemy.sql import func

from api.db import Base

class Deck(Base):
    __tablename__ = 'decks'

    id: Mapped[str] = mapped_column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(1024))
    updated_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now(),
                        onupdate=func.current_timestamp())
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())

    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='decks')

