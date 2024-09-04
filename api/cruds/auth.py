import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

import api.models.user as user_model
import api.schemas.user as user_schema
import api.models.auth as auth_model
import api.utils.auth as auth_util
import api.schemas.auth as auth_schema


async def create_user(
    db: AsyncSession, user_create: user_schema.UserCreate
) -> user_model.User:
    if await is_email_registered(db, user_create.email):
        raise HTTPException(status_code=400, detail="Email is already registered")

    user = user_model.User(
        username=user_create.username,
        email=user_create.email,
        password=auth_util.get_password_hash(user_create.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_state(
    db: AsyncSession, verification_data: auth_schema.Verification
) -> user_model.User:
    stmt = select(user_model.User).filter_by(email=verification_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    await db.commit()
    await db.refresh(user)

    return user

async def is_email_registered(db: AsyncSession, email: str) -> bool:
    stmt = select(user_model.User).filter_by(email=email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user is not None

async def create_verification(
    db: AsyncSession, email: str
) -> auth_model.Verification:
    verification_code = create_verification_code()
    verification = auth_model.Verification(email=email, verification_code=verification_code)
    db.add(verification)
    await db.commit()
    await db.refresh(verification)
    return verification

async def update_verification(
    db: AsyncSession, verification_data: auth_schema.Verification
):
    stmt = select(auth_model.Verification).filter_by(email=verification_data.email)
    result = await db.execute(stmt)
    stored_verification = result.scalar_one_or_none()

    stored_verification.verification_code = create_verification_code()
    db.add(stored_verification)
    await db.commit()
    await db.refresh(stored_verification)


async def delete_verification(
    db: AsyncSession, verification_data: auth_schema.Verification
):
    stmt = select(auth_model.Verification).filter_by(email=verification_data.email)
    result = await db.execute(stmt)
    stored_verification = result.scalar_one_or_none()

    await db.delete(stored_verification)
    await db.commit()


def create_verification_code() -> int:
    return random.randint(100000, 999999)


async def verify_user_code(
    db: AsyncSession, verification_data: auth_schema.Verification
):
    stmt = select(auth_model.Verification).filter_by(email=verification_data.email)
    result = await db.execute(stmt)
    stored_verification = result.scalar_one_or_none()

    if not stored_verification:
        raise HTTPException(status_code=400, detail='Authentication information does not exist')

    if not verification_data.verification_code == stored_verification.verification_code:
        await update_verification(db, verification_data)
        raise HTTPException(status_code=400, detail='Incorrect authentication information')