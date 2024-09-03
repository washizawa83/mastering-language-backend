from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

import api.models.user as user_model
import api.schemas.user as user_schema
import api.utils.auth as auth_util


async def create_user(
    db: AsyncSession, user_create: user_schema.UserCreate
) -> user_model.User:
    if await is_email_registered(db, user_create.email):
        raise HTTPException(status_code=400, detail="Email is already registered")

    user = user_model.User(
        username=user_create.username,
        email=user_create.email,
        password=auth_util.get_password_hash(user_create.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def is_email_registered(db: AsyncSession, email: str) -> bool:
    stmt = select(user_model.User).filter_by(email=email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user is not None
