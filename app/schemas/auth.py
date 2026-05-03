# app/schemas/auth.py
from pydantic import BaseModel, Field, EmailStr


class RegisterRequest(BaseModel):
    """Схема для регистрации нового пользователя."""
    email: EmailStr = Field(..., description="Email адрес пользователя")
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128,  # Добавлено ограничение сверху для безопасности
        description="Пароль (от 8 до 128 символов)"
    )


class TokenResponse(BaseModel):
    """Схема ответа с JWT токеном."""
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field("bearer", description="Тип токена")