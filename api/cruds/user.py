import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv

import api.models.user as user_model
import api.schemas.user as user_schema
import api.schemas.auth as auth_schema
import api.utils.auth as auth_util
from api.db import get_db


load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_user(
    db: AsyncSession, user_id: str
) -> user_model.User:
    stmt = select(user_model.User).filter_by(id=user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user

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


async def authenticate_user(db: AsyncSession, email: str, password: str) -> user_model.User:
    stmt = select(user_model.User).filter_by(email=email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not auth_util.verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> user_model.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=[os.environ.get('ALGORITHM')])
        user_id: str = payload.get('sub')
        if user_id is None:
            raise credentials_exception
        token_data = auth_schema.TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    user = await get_user(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: user_schema.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
