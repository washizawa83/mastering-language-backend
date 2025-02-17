from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import api.schemas.deck as deck_schema
import api.schemas.user as user_schema
import api.cruds.deck as deck_crud
from api.service.auth import get_active_user_permission
from api.db import get_db


router = APIRouter()


@router.get('/deck/{deck_id}', response_model=deck_schema.DeckResponse)
async def get_deck(
    deck_id: str,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    deck = await deck_crud.get_deck(db, deck_id, user.id)
    return deck_schema.DeckResponse.model_validate(deck)


@router.get('/decks', response_model=list[deck_schema.DeckResponse])
async def get_decks(
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    decks = await deck_crud.get_decks(db, user.id)
    return [deck_schema.DeckResponse.model_validate(deck) for deck in decks]


@router.get(
    '/decks-with-card-count',
    response_model=list[deck_schema.DeckWithCardCountResponse] | None,
)
async def get_decks_with_card_count(
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    decks = await deck_crud.get_decks_and_card_count(db, user.id)
    print('#' * 100)
    print(decks)
    return [
        deck_schema.DeckWithCardCountResponse.model_validate(deck)
        for deck in decks
    ]
    return None


@router.post('/deck', response_model=deck_schema.DeckResponse)
async def create_deck(
    form_data: deck_schema.DeckCreate,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    deck = await deck_crud.create_deck(db, form_data, user.id)
    return deck_schema.DeckResponse.model_validate(deck)


@router.put('/deck/{deck_id}', response_model=deck_schema.DeckResponse)
async def update_deck(
    deck_id: str,
    form_data: deck_schema.DeckUpdate,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    deck = await deck_crud.update_deck(db, form_data, deck_id, user.id)
    return deck_schema.DeckResponse.model_validate(deck)


@router.delete('/deck/{deck_id}', response_model=None)
async def delete_deck(
    deck_id: str,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    deck = await deck_crud.get_deck(db, deck_id, user.id)
    return await deck_crud.delete_deck(db, deck)
