from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

import api.models.card as card_model
import api.models.deck as deck_model
import api.schemas.card as card_schema


async def get_card(
    db: AsyncSession, card_id: str, user_id: str
) -> card_model.Card:
    stmt = select(card_model.Card).filter_by(id=card_id)
    result = await db.execute(stmt)
    card = result.scalar_one_or_none()

    if not card:
        raise HTTPException(status_code=404, detail='Deck not found')

    if card.user_id != user_id:
        raise HTTPException(
            status_code=403, detail='You are not authorized to deck.'
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
        raise HTTPException(status_code=404, detail='Deck not found')
    return deck.cards


async def create_card(
    db: AsyncSession,
    form_data: card_schema.CardCreate,
    deck_id: str,
    user_id: str,
):
    card = card_model.Card(
        sentence=form_data.sentence,
        meaning=form_data.meaning,
        image_path=form_data.image_path,
        etymology=form_data.etymology,
        deck_id=deck_id,
        user_id=user_id,
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card


async def delete_card(db: AsyncSession, card: card_model.Card):
    await db.delete(card)
    await db.commit()
