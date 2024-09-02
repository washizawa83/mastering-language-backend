from typing import List

from fastapi import APIRouter

import api.schemas.deck as deck_schema

router = APIRouter()


@router.get("/decks", response_model=List[deck_schema.Deck])
async def list_decks():
    return [deck_schema.Deck(id='test_id1', name='English')]


@router.post("/decks", response_model=deck_schema.Deck)
async def create_deck(body: deck_schema.DeckCreate):
    return deck_schema.Deck(id='test_id2', **body.dict())


@router.put("/decks/{deck_id}", response_model=deck_schema.Deck)
async def update_deck(deck_id: str, body: deck_schema.DeckCreate):
    return deck_schema.Deck(id=deck_id, **body.dict())


@router.delete("/decks/{deck_id}", response_model=None)
async def delete_deck(deck_id: str):
    return
