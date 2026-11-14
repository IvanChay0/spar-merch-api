from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.merch_service import MerchService
from database.dependencies import get_session
from schemas.merch import (
    MerchItemCreate,
    MerchItemUpdate,
    MerchItemResponse,
)

# ⚠️ ЭТА СТРОКА ДОЛЖНА БЫТЬ ЗДЕСЬ, БЕЗ ОТСТУПОВ!
router = APIRouter()


@router.post(
    "/",
    response_model=MerchItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый товар мерча",
)
async def create_merch_item(
    item_data: MerchItemCreate,
    session: AsyncSession = Depends(get_session),
):
    return await MerchService.create(session, item_data)


@router.get(
    "/",
    response_model=list[MerchItemResponse],
    summary="Получить список всех товаров",
)
async def get_all_merch_items(
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    return await MerchService.get_all(session, limit)


@router.get(
    "/{item_id}",
    response_model=MerchItemResponse,
    summary="Получить товар по ID",
)
async def get_merch_item_by_id(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    item = await MerchService.get_by_id(session, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )
    return item


@router.put(
    "/{item_id}",
    response_model=MerchItemResponse,
    summary="Обновить товар",
)
async def update_merch_item(
    item_id: UUID,
    item_data: MerchItemUpdate,
    session: AsyncSession = Depends(get_session),
):
    updated_item = await MerchService.update(session, item_id, item_data)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )
    return updated_item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить товар",
)
async def delete_merch_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    deleted = await MerchService.delete(session, item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )