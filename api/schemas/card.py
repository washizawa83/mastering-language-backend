import uuid
from datetime import datetime

from pydantic import BaseModel, field_serializer


class BaseCard(BaseModel):
    sentence: str
    meaning: str
    image_path: str | None = None
    etymology: str | None = None


class CardCreate(BaseCard):
    pass


class CardResponse(BaseCard):
    id: uuid.UUID
    previous_answer_date: datetime | None = None
    next_answer_date: datetime | None = None
    retention_state: bool
    savings_score: int
    updated_at: datetime
    created_at: datetime
    deck_id: uuid.UUID

    @field_serializer('id')
    def serialize_id(self, id: uuid.UUID) -> str:
        return str(id)

    @field_serializer('previous_answer_date')
    def serialize_previous_answer_date(self, previous_answer_date: datetime):
        if previous_answer_date is not None:
            return previous_answer_date.isoformat()

    @field_serializer('next_answer_date')
    def serialize_next_answer_date(self, next_answer_date: datetime):
        if next_answer_date is not None:
            return next_answer_date.isoformat()

    @field_serializer('updated_at')
    def serialize_updated_at(self, updated_at: datetime):
        return updated_at.isoformat()

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime):
        return created_at.isoformat()

    @field_serializer('deck_id')
    def serialize_deck_id(self, deck_id: uuid.UUID):
        return str(deck_id)
