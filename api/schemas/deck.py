import uuid
from datetime import datetime

from pydantic import BaseModel, model_serializer


class BaseDeck(BaseModel):
    name: str


class DeckCreate(BaseDeck):
    pass


class DeckResponse(BaseDeck):
    id: uuid.UUID
    updated_at: datetime
    created_at: datetime

    @model_serializer
    def serialize(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'updated_at': self.updated_at.isoformat(),
            'created_at': self.created_at.isoformat(),
        }
