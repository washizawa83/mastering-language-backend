from http.client import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

import api.models.deck as deck_model
import api.models.user as user_model
import api.schemas.deck as deck_schema


async def get_deck(
    db: AsyncSession, deck_id: str, user_id: str
) -> deck_model.Deck:
    stmt = select(deck_model.Deck).filter_by(id=deck_id)
    result = await db.execute(stmt)
    deck = result.scalar_one_or_none()

    if not deck:
        raise HTTPException(status_code=404, detail='Deck not found')

    if deck.user_id != user_id:
        raise HTTPException(
            status_code=403, detail='You are not authorized to deck.'
        )

    return deck


async def get_decks(db: AsyncSession, user_id: str) -> list[deck_model.Deck]:
    stmt = (
        select(user_model.User)
        .options(selectinload(user_model.User.decks))
        .filter_by(id=user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user.decks


async def create_deck(
    db: AsyncSession, form_data: deck_schema.DeckCreate, user_id: str
):
    deck = deck_model.Deck(name=form_data.name, user_id=user_id)
    db.add(deck)
    await db.commit()
    await db.refresh(deck)
    return deck


async def delete_deck(db: AsyncSession, deck: deck_model.Deck):
    await db.delete(deck)
    await db.commit()
