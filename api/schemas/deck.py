import uuid
from datetime import datetime

from pydantic import BaseModel, model_serializer


class BaseDeck(BaseModel):
    name: str


class DeckCreate(BaseDeck):
    pass


class DeckUpdate(BaseDeck):
    pass


class DeckResponse(BaseDeck):
    id: uuid.UUID
    updated_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

    @model_serializer
    def serialize(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'updated_at': self.updated_at.isoformat(),
            'created_at': self.created_at.isoformat(),
        }


class DeckWithCardCountModel(BaseModel):
    deck: DeckResponse
    card_count: int
    answer_replay_count: int


class DeckWithCardCountResponse(DeckWithCardCountModel):
    @model_serializer
    def serialize(self):
        return {
            'id': str(self.deck.id),
            'name': self.deck.name,
            'card_count': self.card_count,
            'answer_replay_count': self.answer_replay_count,
            'updated_at': self.deck.updated_at.isoformat(),
            'created_at': self.deck.created_at.isoformat(),
        }
