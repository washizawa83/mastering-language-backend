from datetime import datetime
from zoneinfo import ZoneInfo

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


async def get_answer_replay_cards(
    db: AsyncSession, deck_id: str
) -> list[card_model.Card]:
    stmt = (
        select(card_model.Card)
        .join(card_model.Card.deck)
        .filter(card_model.Card.deck_id == deck_id)
        .filter(
            card_model.Card.next_answer_date
            < datetime.now(ZoneInfo('Asia/Tokyo'))
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()


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


async def update_card_answer(
    db: AsyncSession,
    form_data: card_schema.CardUpdateForAnswerRequest,
    card_id: str,
    user_id: str,
):
    card = await get_card(db, card_id, user_id)
    user_summary = await user_crud.get_user_summary(db, user_id)
    current_saving_score = card.savings_score

    if form_data.is_correct and current_saving_score == 7:
        card.retention_state = True
        user_summary.level_seven_answers += 1
        user_summary.level_seven_correct_answers += 1
        await db.commit()
        await db.refresh(card)
        await db.refresh(user_summary)
        return None

    if form_data.is_correct:
        next_savings_score = current_saving_score + 1
        next_answer_date_delta_seconds = (
            await user_crud.get_answer_date_from_saving_score(
                db, user_id, current_saving_score
            )
        )
        card.savings_score = next_savings_score
        card.next_answer_date = get_next_answer_date(
            next_answer_date_delta_seconds
        )

        match current_saving_score:
            case 1:
                user_summary.level_one_answers += 1
                user_summary.level_one_correct_answers += 1
            case 2:
                user_summary.level_two_answers += 1
                user_summary.level_two_correct_answers += 1
            case 3:
                user_summary.level_three_answers += 1
                user_summary.level_three_correct_answers += 1
            case 4:
                user_summary.level_four_answers += 1
                user_summary.level_four_correct_answers += 1
            case 5:
                user_summary.level_five_answers += 1
                user_summary.level_five_correct_answers += 1
            case 6:
                user_summary.level_six_answers += 1
                user_summary.level_six_correct_answers += 1
            case 7:
                user_summary.level_seven_answers += 1
                user_summary.level_seven_correct_answers += 1
    else:
        next_saving_score = 1
        next_answer_date_delta_seconds = (
            await user_crud.get_answer_date_from_saving_score(
                db, user_id, next_saving_score
            )
        )
        card.savings_score = next_saving_score
        card.next_answer_date = get_next_answer_date(
            next_answer_date_delta_seconds
        )

        match current_saving_score:
            case 1:
                user_summary.level_one_answers += 1
            case 2:
                user_summary.level_two_answers += 1
            case 3:
                user_summary.level_three_answers += 1
            case 4:
                user_summary.level_four_answers += 1
            case 5:
                user_summary.level_five_answers += 1
            case 6:
                user_summary.level_six_answers += 1
            case 7:
                user_summary.level_seven_answers += 1

    await db.commit()
    await db.refresh(card)
    await db.refresh(user_summary)
    return None


async def delete_card(db: AsyncSession, card: card_model.Card):
    await db.delete(card)
    await db.commit()
