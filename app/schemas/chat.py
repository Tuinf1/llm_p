# app/schemas/chat.py
from pydantic import BaseModel, Field,  ConfigDict
from typing import Optional

from datetime import datetime

class ChatRequest(BaseModel):
    """Схема запроса к чату с ИИ"""
    prompt: str = Field(..., description="Основной текст запроса пользователя")
    system: Optional[str] = Field(None, description="Необязательная системная инструкция для модели")
    max_history: int = Field(5, ge=0, le=50, description="Количество последних сообщений из истории диалога")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Уровень креативности модели (0.0 — детерминировано, 2.0 — максимально случайно)")


class ChatResponse(BaseModel):
    """Схема ответа от чата с ИИ"""
    answer: str = Field(..., description="Ответ модели на запрос пользователя")



# для сохранения промта (не строго по заданию)
class MessagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime  # 