from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class MerchItemCreate(BaseModel):
    """Схема для создания нового товара."""
    name: str = Field(..., example="Худи Spar", description="Название товара")
    price: float = Field(..., gt=0, example=300.0, description="Цена в монетах")
    description: Optional[str] = Field(None, example="Стильное худи с логотипом")


class MerchItemUpdate(BaseModel):
    """Схема для обновления товара."""
    name: str = Field(..., example="Худи Spar Premium")
    price: float = Field(..., gt=0, example=350.0)
    description: Optional[str] = None


class MerchItemResponse(BaseModel):
    """Схема ответа с данными товара."""
    id: UUID
    name: str
    price: float
    description: Optional[str] = None

    class Config:
        from_attributes = True  # Для работы с ORM-объектами