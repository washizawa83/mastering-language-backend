from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import api.schemas.auth as auth_schema
import api.schemas.user as user_schema
import api.cruds.user as user_crud
import api.cruds.auth as auth_crud
import api.utils.env as env
from api.db import get_db
from api.service.auth import get_active_user_permission


router = APIRouter()


@router.post('/signup', response_model=bool)
async def signup(
    form_data: auth_schema.SignupRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    new_user = await user_crud.create_user(db, form_data)
    await auth_crud.create_verification(db, new_user.email)
    return new_user is not None


@router.post('/signup-verify', response_model=str | None)
async def signup_verify(
    body: auth_schema.Verification, db: AsyncSession = Depends(get_db)
):
    await auth_crud.verify_user_code(db, body)

    await auth_crud.delete_verification(db, body)
    active_user = await user_crud.update_user_state(db, body)
    return active_user.username


@router.get('/verify', response_model=None)
async def verify(
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    if not user:
        raise credentials_exception
    return None


@router.post('/login')
async def login_for_access_token(
    form_data: auth_schema.EmailPasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> auth_schema.Token:
    user = await user_crud.authenticate_user(db, form_data)
    access_token_expires = timedelta(
        minutes=int(env.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    access_token = auth_crud.create_access_token(
        data={'sub': user.id}, expires_delta=access_token_expires
    )
    return auth_schema.Token(access_token=access_token, token_type='bearer')
