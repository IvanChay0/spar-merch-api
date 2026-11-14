from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class TokenResponse(BaseModel):
    """Ответ с JWT токенами."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class EmployeeResponse(BaseModel):
    """Ответ с данными сотрудника (без пароля!)."""
    id: UUID
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    coins_amount: float

    class Config:
        from_attributes = True


class InventoryItemResponse(BaseModel):
    """Ответ с информацией о купленном товаре."""
    purchase_id: UUID
    date: datetime
    item_name: str
    price: float


class StandardResponse(BaseModel):
    """Стандартный ответ с сообщением."""
    message: str