from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import api.schemas.user as user_schema
import api.cruds.auth as user_cruds
from api.db import get_db

router = APIRouter()


@router.post('/signup', response_model=bool)
async def signup(
    body: user_schema.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    new_user = await user_cruds.create_user(db, body)
    return new_user is not None
