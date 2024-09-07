import random
from datetime import datetime, timezone, timedelta
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from jose import jwt

import api.models.auth as auth_model
import api.schemas.auth as auth_schema
import api.utils.mail as mail_util
import api.utils.env as env


@mail_util.after_verification_send_mail_decorator
async def create_verification(
    db: AsyncSession, email: str
) -> auth_model.Verification:
    verification_code = create_verification_code()
    verification = auth_model.Verification(
        email=email, verification_code=verification_code
    )
    db.add(verification)
    await db.commit()
    await db.refresh(verification)
    return verification


@mail_util.after_verification_send_mail_decorator
async def update_verification(
    db: AsyncSession, verification_data: auth_schema.Verification
) -> auth_model.Verification:
    stmt = select(auth_model.Verification).filter_by(
        email=verification_data.email
    )
    result = await db.execute(stmt)
    stored_verification = result.scalar_one_or_none()

    stored_verification.verification_code = create_verification_code()
    db.add(stored_verification)
    await db.commit()
    await db.refresh(stored_verification)
    return stored_verification


async def delete_verification(
    db: AsyncSession, verification_data: auth_schema.Verification
):
    stmt = select(auth_model.Verification).filter_by(
        email=verification_data.email
    )
    result = await db.execute(stmt)
    stored_verification = result.scalar_one_or_none()

    await db.delete(stored_verification)
    await db.commit()


def create_verification_code() -> int:
    return random.randint(100000, 999999)


async def verify_user_code(
    db: AsyncSession, verification_data: auth_schema.Verification
):
    stmt = select(auth_model.Verification).filter_by(
        email=verification_data.email
    )
    result = await db.execute(stmt)
    stored_verification = result.scalar_one_or_none()

    if not stored_verification:
        raise HTTPException(
            status_code=400, detail='Authentication information does not exist'
        )

    if (
        not verification_data.verification_code
        == stored_verification.verification_code
    ):
        await update_verification(db, verification_data)
        raise HTTPException(
            status_code=400, detail='Incorrect authentication information'
        )


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    data = {
        k: (v.hex if isinstance(v, uuid.UUID) else v) for k, v in data.items()
    }
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, env.SECRET_KEY, algorithm=env.ALGORITHM)
    return encoded_jwt
