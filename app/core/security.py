# app/core/security.py
from llm_p.app.core.config import settings
# --- Хак для совместимости passlib и bcrypt 4.x ---
import bcrypt
try:
    import types
    bcrypt.__about__ = types.ModuleType('__about__')
    bcrypt.__about__.__version__ = bcrypt.__version__
except AttributeError:
    pass
# -----------------------------------------------

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Optional, Dict, Any
import warnings

# Игнорируем предупреждения о версии bcrypt
warnings.filterwarnings("ignore", message=".*trapped error reading bcrypt version.*")

# Импортируем настройки из .env


# Настройка контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаёт JWT access token.
    
    Args:
        data: Словарь с данными (например, {"sub": user_id})
        expires_delta: Время жизни токена
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Берем время жизни из настроек .env
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    
    # Используем секрет и алгоритм ИЗ НАСТРОЕК (.env)
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Декодирует JWT токен.
    """
    try:
        # Используем секрет и алгоритм ИЗ НАСТРОЕК (.env)
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")
    
    
# def get_current_user_from_token(token: str) -> Dict[str, Any]:
#     """
#     Извлекает информацию о пользователе из токена.
    
#     Args:
#         token: JWT токен
        
#     Returns:
#         Словарь с данными пользователя (sub, role)
        
#     Raises:
#         JWTError: Если токен просрочен или невалиден
#     """
#     payload = decode_access_token(token)
#     return {
#         "user_id": payload.get("sub"),
#         "role": payload.get("role")
#     }