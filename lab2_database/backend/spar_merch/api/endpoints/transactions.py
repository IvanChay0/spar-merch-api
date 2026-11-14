from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_session
from schemas.requests import SendCoinsRequest
from schemas.responses import StandardResponse
from api.services import transaction_service
from api.dependencies import get_current_employee
from database.tables.entities.employee import Employee

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "/buy/{item_id}",
    response_model=StandardResponse,
    summary="Купить товар за монеты",
)
async def buy_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_employee: Employee = Depends(get_current_employee),
):
    """
    Покупка товара из каталога за бонусные монеты.
    Проверяет наличие товара и достаточность баланса.
    """
    try:
        result = await transaction_service.buy_merch_item(
            session, current_employee, item_id
        )
        return result
    except ValueError as e:
        error_msg = str(e)
        if "не найден" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        elif "недостаточно" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )


@router.post(
    "/send_coins",
    response_model=StandardResponse,
    summary="Перевести монеты другому сотруднику",
)
async def send_coins(
    request: SendCoinsRequest,
    session: AsyncSession = Depends(get_session),
    current_employee: Employee = Depends(get_current_employee),
):
    """
    Перевод бонусных монет другому сотруднику по username.
    """
    try:
        result = await transaction_service.transfer_coins(
            session,
            current_employee,
            request.gainer_username,
            request.amount,
        )
        return result
    except ValueError as e:
        error_msg = str(e)
        if "не найден" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )