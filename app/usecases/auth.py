from datetime import timedelta

from llm_p.app.repositories.users import UserRepository
from llm_p.app.schemas.user import UserPublic
from llm_p.app.schemas.auth import RegisterRequest, TokenResponse  # ← используем правильные схемы
from llm_p.app.core.errors import ConflictError, UnauthorizedError, NotFoundError
from llm_p.app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token
)
from llm_p.app.core.config import settings  # ← чтобы взять ACCESS_TOKEN_EXPIRE_MINUTES


class AuthUseCase:
    """Use case для управления аутентификацией пользователей."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def register(self, user_data: RegisterRequest) -> UserPublic:
        """
        Регистрация нового пользователя.
        
        Проверяет уникальность email, хеширует пароль и создает пользователя.
        
        Args:
            user_data: Данные для регистрации пользователя
            
        Returns:
            UserPublic: Созданный пользователь без пароля
            
        Raises:
            ConflictError: Если email уже занят
        """
        # Проверяем, не занят ли email
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ConflictError(f"User with email {user_data.email} already exists")
        
        # Хешируем пароль
        hashed_password = hash_password(user_data.password)
        
        # Создаем пользователя через репозиторий
        user = await self.user_repository.create(
            user_in=user_data,
            password_hash=hashed_password  # ← обратите внимание: поле называется password_hash в модели        )
        )
        # Возвращаем публичную версию пользователя (без пароля)
        return UserPublic.model_validate(user)
    
    async def login(self, email: str, password: str) -> TokenResponse:
        """
        Вход пользователя в систему.
        
        Ищет пользователя по email, проверяет пароль и генерирует JWT токен.
        
        Args:
            email: Email пользователя
            password: Пароль пользователя
            
        Returns:
            TokenResponse: Словарь с access_token и token_type
            
        Raises:
            UnauthorizedError: Если email не существует или пароль неверный
        """
        # Ищем пользователя по email
        user = await self.user_repository.get_by_email(email)
        
        # Если пользователь не найден или пароль неверный
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")
        
        # Генерируем JWT токен
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role}, 
            expires_delta=access_token_expires
        )
        
        return TokenResponse(access_token=access_token, token_type="bearer")
    
    async def get_profile(self, user_id: int) -> UserPublic:
        """
        Получение профиля пользователя по ID.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserPublic: Публичные данные пользователя
            
        Raises:
            NotFoundError: Если пользователь не найден
        """
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")
        
        return UserPublic.model_validate(user)