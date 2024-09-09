from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

import api.models.user as user_model
import api.schemas.auth as auth_schema
import api.utils.auth as auth_util
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
