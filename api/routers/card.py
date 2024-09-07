from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import api.schemas.card as card_schema
import api.schemas.user as user_schema
import api.cruds.card as card_crud
from api.service.auth import get_active_user_permission
from api.db import get_db


router = APIRouter()


@router.get('/card/{card_id}', response_model=card_schema.CardResponse)
async def get_card(
    card_id: str,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    card = await card_crud.get_card(db, card_id, user.id)
    return card_schema.CardResponse.model_validate(card)


@router.get('/cards/{deck_id}', response_model=list[card_schema.CardResponse])
async def get_cards(
    deck_id: str,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    cards = await card_crud.get_cards(db, deck_id)
    return [card_schema.CardResponse.model_validate(card) for card in cards]


@router.post('/card{deck_id}', response_model=card_schema.CardResponse)
async def create_card(
    deck_id: str,
    form_data: card_schema.CardCreate = Depends(),
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    card = await card_crud.create_card(db, form_data, deck_id, user.id)
    return card_schema.CardResponse.model_validate(card)


@router.delete('/card/{card_id', response_model=None)
async def delete_card(
    card_id: str,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    card = await card_crud.get_card(db, card_id, user.id)
    return await card_crud.delete_card(db, card)
