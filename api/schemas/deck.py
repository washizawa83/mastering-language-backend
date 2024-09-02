from pydantic import BaseModel


class DeckBase(BaseModel):
    name: str


class Deck(DeckBase):
    id: str

    class Config:
        orm_mode = True


class DeckCreate(DeckBase):
    pass
