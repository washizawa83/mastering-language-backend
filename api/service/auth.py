from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

import api.utils.env as env
from api.schemas.auth import TokenData
from api.db import get_db
from api.cruds.user import get_user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def get_user_id_by_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, env.SECRET_KEY, algorithms=[env.ALGORITHM])
        user_id: str = payload.get('sub')
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception from None
    return token_data


async def get_active_user_permission(
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(get_user_id_by_token),
):
    user = await get_user(db, token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Inactive user'
        )
    return user
