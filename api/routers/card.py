import uuid
import base64

from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import api.schemas.card as card_schema
import api.schemas.user as user_schema
import api.cruds.card as card_crud
import api.utils.env as env
from api.utils.aws import get_s3_client
from api.service.auth import get_active_user_permission
from api.db import get_db


router = APIRouter()


@router.get('/card/{card_id}', response_model=card_schema.CardResponse)
async def get_card(
    card_id: str,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    card = await card_crud.get_card(db, card_id, user.id)
    return card_schema.CardResponse.model_validate(card)


@router.get('/cards/{deck_id}', response_model=list[card_schema.CardResponse])
async def get_cards(
    deck_id: str,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    cards = await card_crud.get_cards(db, deck_id)
    return [card_schema.CardResponse.model_validate(card) for card in cards]


@router.post('/card/{deck_id}', response_model=card_schema.CardResponse)
async def create_card(
    deck_id: str,
    form_data: card_schema.CardCreate,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    card = await card_crud.create_card(db, form_data, deck_id, user.id)
    return card_schema.CardResponse.model_validate(card)


@router.put('/card/{card_id}', response_model=card_schema.CardResponse)
async def update_card(
    card_id: str,
    form_data: card_schema.CardUpdate,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    card = await card_crud.update_card(db, form_data, card_id, user.id)
    return card_schema.CardResponse.model_validate(card)


@router.delete('/card/{card_id}', response_model=None)
async def delete_card(
    card_id: str,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    card = await card_crud.get_card(db, card_id, user.id)
    return await card_crud.delete_card(db, card)


@router.get('/download-card-image/{card_id}')
async def download_card_image(
    card_id: str,
    db: AsyncSession = Depends(get_db),
    user: user_schema.User = Depends(get_active_user_permission),
):
    card = await card_crud.get_card(db, card_id, user.id)
    bucket = env.S3_BUCKET_NAME
    s3_client = get_s3_client()

    try:
        s3_object = s3_client.get_object(Bucket=bucket, Key=card.image_path)
        image_data = s3_object['Body'].read()
        return base64.b64encode(image_data).decode('utf-8')
    except s3_client.exceptions.NoSuchKey:
        return HTTPException(status_code=404, detail='Image not found')
    except Exception as e:
        return HTTPException(
            status_code=500, detail=f'Error retrieving image: {str(e)}'
        )


@router.post('/upload-card-image/{deck_id}', response_model=str)
async def upload_card_image(
    deck_id: str,
    upload_image: UploadFile,
    user: user_schema.User = Depends(get_active_user_permission),
):
    upload_file_name = '{uuid}-{file_name}'.format(
        uuid=str(uuid.uuid4()), file_name=upload_image.filename
    )
    key = 'cards/images/{deck_id}/{file_name}'.format(
        deck_id=deck_id, file_name=upload_file_name
    )
    bucket = env.S3_BUCKET_NAME

    s3_client = get_s3_client()

    try:
        s3_client.put_object(Key=key, Bucket=bucket, Body=upload_image.file)
        return key
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'S3 Upload Error: {e}',
        )
