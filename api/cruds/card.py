from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

import api.models.card as card_model
import api.models.deck as deck_model
import api.schemas.card as card_schema
import api.cruds.user as user_crud
from api.utils.oblivion_curve import get_next_answer_date
from api.cruds.common import get_model_by_id


async def get_card(
    db: AsyncSession, card_id: str, user_id: str
) -> card_model.Card:
    card = await get_model_by_id(db, card_model.Card, card_id)

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Deck not found'
        )

    if card.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to deck.',
        )

    return card


async def get_cards(db: AsyncSession, deck_id: str) -> list[card_model.Card]:
    stmt = (
        select(deck_model.Deck)
        .options(selectinload(deck_model.Deck.cards))
        .filter_by(id=deck_id)
    )
    result = await db.execute(stmt)
    deck = result.scalar_one_or_none()

    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Deck not found'
        )
    return deck.cards


async def create_card(
    db: AsyncSession,
    form_data: card_schema.CardCreate,
    deck_id: str,
    user_id: str,
):
    user_settings = await user_crud.get_user_settings(db, user_id)
    card = card_model.Card(
        sentence=form_data.sentence,
        meaning=form_data.meaning,
        image_path=form_data.image_path,
        etymology=form_data.etymology,
        deck_id=deck_id,
        user_id=user_id,
        next_answer_date=get_next_answer_date(user_settings.level_one),
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card


async def update_card(
    db: AsyncSession,
    form_data: card_schema.CardUpdate,
    card_id: str,
    user_id: str,
):
    card = await get_card(db, card_id, user_id)
    card.sentence = form_data.sentence
    card.meaning = form_data.meaning
    card.image_path = form_data.image_path
    card.etymology = form_data.etymology
    await db.commit()
    await db.refresh(card)
    return card


async def delete_card(db: AsyncSession, card: card_model.Card):
    await db.delete(card)
    await db.commit()
