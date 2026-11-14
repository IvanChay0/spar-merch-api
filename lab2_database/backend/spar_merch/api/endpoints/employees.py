from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_session
from schemas.responses import EmployeeResponse, InventoryItemResponse
from api.services import employee_service
from api.dependencies import get_current_employee
from database.tables.entities.employee import Employee

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get(
    "/me",
    response_model=EmployeeResponse,
    summary="Получить профиль текущего сотрудника",
)
async def get_my_profile(
    current_employee: Employee = Depends(get_current_employee),
):
    """Возвращает данные текущего аутентифицированного сотрудника."""
    return current_employee


@router.get(
    "/me/wallet",
    summary="Получить баланс монет текущего сотрудника",
)
async def get_my_wallet(
    current_employee: Employee = Depends(get_current_employee),
):
    """Возвращает текущий баланс монет сотрудника."""
    return {
        "username": current_employee.username,
        "coins_amount": current_employee.coins_amount,
    }


@router.get(
    "/me/inventory",
    response_model=list[InventoryItemResponse],
    summary="Получить инвентарь (купленные товары) текущего сотрудника",
)
async def get_my_inventory(
    session: AsyncSession = Depends(get_session),
    current_employee: Employee = Depends(get_current_employee),
):
    """Возвращает список всех купленных товаров с датами покупок."""
    inventory = await employee_service.get_employee_inventory(
        session, current_employee.id
    )
    return inventory