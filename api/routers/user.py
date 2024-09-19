from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import api.schemas.user as user_schema
import api.cruds.user as user_crud
from api.db import get_db
from api.service.auth import get_active_user_permission


router = APIRouter()


@router.get('/user', response_model=user_schema.UserResponse)
async def get_user(
    user: user_schema.User = Depends(get_active_user_permission),
):
    return user_schema.UserResponse.model_validate(user)


@router.get('/user-settings', response_model=user_schema.UserSettingsResponse)
async def get_user_settings(
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    return await user_crud.get_user_settings(db, user.id)


@router.put('/user-settings', response_model=None)
async def update_user_settings(
    form_data: user_schema.UserSettingsRequest,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    await user_crud.update_user_settings(db, user.id, form_data)
