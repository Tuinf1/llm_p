# app/repositories/chat_messages.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from llm_p.app.db.models import ChatMessage


class ChatMessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_message(self, message: ChatMessage) -> ChatMessage:
        """Добавляет сообщение в базу данных."""
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_user_history(self, user_id: int, limit: int) -> list[ChatMessage]:
        """
        Получает последние N сообщений пользователя.
        Возвращает список в хронологическом порядке (старые → новые).
        """
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        # Разворачиваем, чтобы старые были первыми
        messages.reverse()
        return messages

    async def clear_user_history(self, user_id: int) -> None:
        """Удаляет всю историю чата для пользователя."""
        await self.session.execute(
            delete(ChatMessage).where(ChatMessage.user_id == user_id)
        )
        await self.session.commit()