from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from database.dependencies import get_session
from database.tables.entities.employee import Employee
from core.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/sign_in")


async def get_current_employee(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session)
) -> Employee:
    """
    Зависимость для получения текущего сотрудника из JWT токена.
    Используется в защищенных эндпоинтах.
    """
    from sqlalchemy import select

    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employee_id = payload.get("sub")
    if employee_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не содержит ID сотрудника",
        )

    result = await session.execute(select(Employee).where(Employee.id == UUID(employee_id)))
    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудник не найден",
        )

    return employee