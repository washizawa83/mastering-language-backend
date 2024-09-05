from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import api.schemas.user as user_schema
import api.schemas.auth as auth_schema
import api.cruds.user as user_cruds
import api.cruds.auth as auth_cruds
from api.db import get_db

router = APIRouter()


@router.post('/signup', response_model=bool)
async def signup(
    body: user_schema.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    new_user = await user_cruds.create_user(db, body)
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
