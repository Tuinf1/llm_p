from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_p.app.db.models import User
# Важно: используем схему из задания, которая реально существует
from llm_p.app.schemas.auth import RegisterRequest 


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    async def get_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    async def create(self, user_in: RegisterRequest, password_hash: str) -> User:
        """
        Создать нового пользователя в БД.
        
        Args:
            user_in: Схема с данными пользователя (email и т.д.)
            password_hash: Уже захешированный пароль (приходит из UseCase)
            
        Returns:
            User: Созданный ORM-объект
        """
        # Извлекаем данные из схемы, исключая пароль (так как он уже захеширован отдельно)
        user_data = user_in.model_dump(exclude={'password'}, exclude_unset=True)
        
        # Добавляем хешированный пароль в правильное поле модели
        user_data['password_hash'] = password_hash
        
        # Опционально: если в модели есть поле role, зададим дефолтное значение
        if 'role' not in user_data:
            user_data['role'] = 'user' 

        # Создаём ORM-объект
        db_user = User(**user_data)
        
        # Добавляем в сессию
        self.session.add(db_user)
        
        # Фиксируем изменения
        await self.session.commit()
        
        # Обновляем объект (чтобы получить autoincrement id и другие значения из БД)
        await self.session.refresh(db_user)
        
        return db_user