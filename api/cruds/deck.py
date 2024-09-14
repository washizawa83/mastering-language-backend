from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, aliased
from fastapi import HTTPException, status

import api.models.deck as deck_model
import api.models.card as card_model
import api.models.user as user_model
import api.schemas.deck as deck_schema
from api.cruds.common import get_model_by_id


async def get_deck(
    db: AsyncSession, deck_id: str, user_id: str
) -> deck_model.Deck:
    deck = await get_model_by_id(db, deck_model.Deck, deck_id)

    if not deck:
        raise HTTPException(status_code=404, detail='Deck not found')

    if deck.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to deck.',
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )
    return user.decks


async def get_decks_and_card_count(
    db: AsyncSession, user_id: str
) -> list[deck_schema.DeckWithCardCountModel]:
    Deck = aliased(deck_model.Deck)
    Card = aliased(card_model.Card)

    stmt = (
        select(Deck, func.count(Card.id).label('card_count'))
        .join(Card, Deck.id == Card.deck_id, isouter=True)
        .filter(Deck.user_id == user_id)
        .group_by(Deck.id)
    )

    result = await db.execute(stmt)
    decks_with_card_count = result.all()

    if not decks_with_card_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User or Deck not found',
        )

    return [
        {'deck': deck, 'card_count': card_count}
        for deck, card_count in decks_with_card_count
    ]


async def create_deck(
    db: AsyncSession, form_data: deck_schema.DeckCreate, user_id: str
):
    deck = deck_model.Deck(name=form_data.name, user_id=user_id)
    db.add(deck)
    await db.commit()
    await db.refresh(deck)
    return deck


async def update_deck(
    db: AsyncSession,
    form_data: deck_schema.DeckUpdate,
    deck_id: str,
    user_id: str,
):
    deck = await get_deck(db, deck_id, user_id)
    deck.name = form_data.name
    await db.commit()
    await db.refresh(deck)
    return deck


async def delete_deck(db: AsyncSession, deck: deck_model.Deck):
    await db.delete(deck)
    await db.commit()
