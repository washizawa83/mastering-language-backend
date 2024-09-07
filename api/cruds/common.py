from typing import Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import api.models.user as user_model


T = TypeVar('T')


async def get_model_by_id(
    db: AsyncSession, model: Type[T], model_id: str
) -> T | None:
    stmt = select(model).filter_by(id=model_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(user_model.User).filter_by(email=email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
