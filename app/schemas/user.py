# app/schemas/user.py
from pydantic import BaseModel, ConfigDict


class UserPublic(BaseModel):
    """Публичная схема пользователя — без пароля и чувствительных данных"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: str

    