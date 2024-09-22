import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

import api.models.user as user_model
import api.schemas.auth as auth_schema
import api.schemas.user as user_schema
import api.utils.auth as auth_util
import api.utils.oblivion_curve as oblivion_curve_util
from api.cruds.common import get_model_by_id, get_user_by_email


async def get_user(db: AsyncSession, user_id: str) -> user_model.User:
    user = await get_model_by_id(db, user_model.User, user_id)
    return user


async def create_user(
    db: AsyncSession, form_data: auth_schema.SignupRequestForm
) -> user_model.User:
    if await is_email_registered(db, form_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email is already registered',
        )

    user = user_model.User(
        username=form_data.username,
        email=form_data.email,
        password=auth_util.get_password_hash(form_data.password),
    )

    async with db:
        db.add(user)
        await db.commit()
        await db.refresh(user)

    async with db:
        await create_user_settings(db, user.id)

    async with db:
        await create_user_summaries(db, user.id)

    return user


async def create_user_settings(db: AsyncSession, user_id: uuid.UUID):
    user_settings = user_model.UserSettings(user_id=user_id)
    db.add(user_settings)
    await db.commit()


async def create_user_summaries(db: AsyncSession, user_id: uuid.UUID):
    user_summaries = user_model.UserSummary(user_id=user_id)
    db.add(user_summaries)
    await db.commit()


async def update_user_state(
    db: AsyncSession, verification_data: auth_schema.Verification
) -> user_model.User:
    stmt = select(user_model.User).filter_by(email=verification_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    user.is_active = True
    await db.commit()
    await db.refresh(user)

    return user


async def authenticate_user(
    db: AsyncSession, form_data: auth_schema.EmailPasswordRequestForm
) -> user_model.User:
    user = await get_user_by_email(db, form_data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )
    if not auth_util.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return user


async def is_email_registered(db: AsyncSession, email: str) -> bool:
    user = await get_user_by_email(db, email)
    return user is not None


async def get_user_settings(
    db: AsyncSession, user_id: str
) -> user_model.UserSettings:
    stmt = (
        select(user_model.User)
        .options(selectinload(user_model.User.user_settings))
        .filter_by(id=user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user.user_settings


async def get_user_summary(
    db: AsyncSession, user_id: str
) -> user_model.UserSummary:
    stmt = (
        select(user_model.User)
        .options(selectinload(user_model.User.user_summaries))
        .filter_by(id=user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user.user_summaries


async def get_answer_date_from_saving_score(
    db: AsyncSession, user_id: str, saving_score: int
) -> int:
    user_settings = await get_user_settings(db, user_id)

    level_mapping = {
        1: user_settings.level_one,
        2: user_settings.level_two,
        3: user_settings.level_three,
        4: user_settings.level_four,
        5: user_settings.level_five,
        6: user_settings.level_six,
    }
    return level_mapping.get(saving_score, user_settings.level_seven)


async def get_user_summary_update_level(
    user_summary: user_model.UserSummary, saving_score: int
):
    user_summary_update_level_mapping = {
        1: [
            user_summary.level_one_answers,
            user_summary.level_one_correct_answers,
        ],
        2: [
            user_summary.level_two_answers,
            user_summary.level_two_correct_answers,
        ],
        3: [
            user_summary.level_three_answers,
            user_summary.level_three_correct_answers,
        ],
        4: [
            user_summary.level_four_answers,
            user_summary.level_four_correct_answers,
        ],
        5: [
            user_summary.level_five_answers,
            user_summary.level_five_correct_answers,
        ],
        6: [
            user_summary.level_six_answers,
            user_summary.level_six_correct_answers,
        ],
        7: [
            user_summary.level_seven_answers,
            user_summary.level_seven_correct_answers,
        ],
    }

    return user_summary_update_level_mapping.get(saving_score)


async def update_user_settings(
    db: AsyncSession, user_id: str, form_data: user_schema.UserSettingsRequest
):
    stmt = (
        select(user_model.User)
        .options(selectinload(user_model.User.user_settings))
        .filter_by(id=user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    user_settings = user.user_settings

    levels = [
        'level_one',
        'level_two',
        'level_three',
        'level_four',
        'level_five',
        'level_six',
        'level_seven',
    ]

    for level in levels:
        oblivion_curve_date = getattr(form_data, level)
        result = oblivion_curve_util.get_next_answer_date_delta_seconds(
            oblivion_curve_date['month'],
            oblivion_curve_date['day'],
            oblivion_curve_date['hour'],
        )
        setattr(user_settings, level, result)

    await db.commit()
    await db.refresh(user_settings)
