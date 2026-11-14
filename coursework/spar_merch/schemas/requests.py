from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SignUpRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="ivan_petrov")
    password: str = Field(..., min_length=6, max_length=72, example="securePassword123")
    email: Optional[EmailStr] = Field(None, example="ivan@spar.ru")
    phone: Optional[str] = Field(None, example="+79001234567")

class SignInRequest(BaseModel):
    """Схема для входа (аутентификации)."""
    username: str = Field(..., example="ivan_petrov")
    password: str = Field(..., example="securePassword123")


class RefreshTokenRequest(BaseModel):
    """Схема для обновления access токена."""
    refresh_token: str


class SendCoinsRequest(BaseModel):
    """Схема для перевода монет другому сотруднику."""
    gainer_username: str = Field(..., example="maria_sidorova")
    amount: float = Field(..., gt=0, example=50.0)