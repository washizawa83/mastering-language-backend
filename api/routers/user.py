from fastapi import APIRouter, Depends

import api.schemas.user as user_schema
from api.service.auth import get_active_user_permission


router = APIRouter()


@router.get('/user', response_model=user_schema.UserResponse)
async def get_user(
    user: user_schema.User = Depends(get_active_user_permission),
):
    return user_schema.UserResponse(username=user.username).model_dump()
