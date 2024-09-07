from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import api.schemas.user as user_schema
import api.schemas.auth as auth_schema
import api.cruds.user as user_cruds
import api.cruds.auth as auth_cruds
import api.utils.env as env
from api.db import get_db


router = APIRouter()


@router.post('/signup', response_model=bool)
async def signup(
    form_data: auth_schema.SignupRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    new_user = await user_cruds.create_user(db, form_data)
    await auth_cruds.create_verification(db, new_user.email)
    return new_user is not None


@router.post('/verification', response_model=str | None)
async def verification(
        body: auth_schema.Verification,
        db: AsyncSession = Depends(get_db)
):
    await auth_cruds.verify_user_code(db, body)

    await auth_cruds.delete_verification(db, body)
    active_user = await user_cruds.update_user_state(db, body)
    return active_user.username


@router.post('/login')
async def login_for_access_token(
    form_data: auth_schema.EmailPasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> auth_schema.Token:
    user = await user_cruds.authenticate_user(db, form_data)
    access_token_expires = timedelta(
        minutes=int(
            env.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )
    access_token = auth_cruds.create_access_token(
        data={'sub': user.id}, expires_delta=access_token_expires
    )
    return auth_schema.Token(access_token=access_token, token_type='bearer').model_dump()
