from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_session
from schemas.requests import SignUpRequest, SignInRequest
from schemas.responses import TokenResponse, EmployeeResponse
from api.services import auth_service
from core.jwt import decode_token
from database.tables.entities.employee import Employee
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/sign_up",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового сотрудника",
)
async def sign_up(
        user_data: SignUpRequest,
        session: AsyncSession = Depends(get_session),
):
    """
    Регистрация нового сотрудника в системе.
    После регистрации начисляется стартовый баланс 1000 монет.
    """
    try:
        employee = await auth_service.register_user(session, user_data.model_dump())
        return employee
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/sign_in",
    response_model=TokenResponse,
    summary="Вход в систему (аутентификация)",
)
async def sign_in(
        credentials: SignInRequest,
        session: AsyncSession = Depends(get_session),
):
    """
    Аутентификация сотрудника по логину и паролю.
    Возвращает пару JWT токенов (access + refresh).
    """
    employee = await auth_service.authenticate_user(
        session, credentials.username, credentials.password
    )

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = await auth_service.generate_tokens(session, employee)
    return tokens


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Обновление access токена",
)
async def refresh_token(
        session: AsyncSession = Depends(get_session),
):
    """
    Обновление access токена с использованием refresh токена из заголовка.
    """
    # В реальном приложении здесь была бы логика проверки refresh токена
    # Для упрощения возвращаем ошибку (нужно доработать)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Функционал обновления токена будет реализован позже",
    )