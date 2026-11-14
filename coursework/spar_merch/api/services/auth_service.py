from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.tables.entities.employee import Employee
from core.security import get_password_hash, verify_password
from core.jwt import create_access_token, create_refresh_token
from schemas.requests import SignUpRequest  # Создадим эту схему на следующем шаге


async def authenticate_user(session: AsyncSession, username: str, password: str) -> Employee | None:
    """Проверяет логин и пароль. Возвращает сотрудника или None."""
    result = await session.execute(select(Employee).where(Employee.username == username))
    employee = result.scalar_one_or_none()

    if not employee or not verify_password(password, employee.password):
        return None
    return employee


async def register_user(session: AsyncSession, user_data: dict) -> Employee:
    """Регистрирует нового сотрудника."""
    # Проверяем, не занят ли username
    existing = await session.execute(select(Employee).where(Employee.username == user_data["username"]))
    if existing.scalar_one_or_none():
        raise ValueError("Сотрудник с таким username уже существует")

    hashed_password = get_password_hash(user_data["password"])

    new_employee = Employee(
        username=user_data["username"],
        password=hashed_password,
        email=user_data.get("email"),
        phone=user_data.get("phone"),
        coins_amount=1000.0  # Стартовый баланс
    )
    session.add(new_employee)
    await session.commit()
    await session.refresh(new_employee)
    return new_employee


async def generate_tokens(session: AsyncSession, employee: Employee) -> dict:
    """Генерирует пару токенов и сохраняет refresh_token в БД."""
    from datetime import timedelta
    from core.config import get_settings

    settings = get_settings()

    access_token = create_access_token(
        data={"sub": str(employee.id), "username": employee.username}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(employee.id)},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_LIFETIME_DAYS)
    )

    # Сохраняем refresh_token в БД для возможности отзыва (logout)
    employee.refresh_token = refresh_token
    await session.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }