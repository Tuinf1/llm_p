# app/core/errors.py

class AppError(Exception):
    """Базовое исключение для приложения."""
    pass


class ConflictError(AppError):
    """Ошибка конфликта (например, email уже существует)."""
    
    def __init__(self, message: str = "Конфликт ресурсов"):
        self.message = message
        super().__init__(self.message)


class UnauthorizedError(AppError):
    """Ошибка авторизации (неверный пароль или токен)."""
    
    def __init__(self, message: str = "Неавторизован"):
        self.message = message
        super().__init__(self.message)


class ForbiddenError(AppError):
    """Ошибка доступа (нет прав на выполнение операции)."""
    
    def __init__(self, message: str = "Доступ запрещен"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(AppError):
    """Ошибка отсутствия объекта (объект в базе не найден)."""
    
    def __init__(self, message: str = "Объект не найден"):
        self.message = message
        super().__init__(self.message)


class ExternalServiceError(AppError):
    """Ошибка внешнего сервиса (например, OpenRouter вернул ошибку)."""
    
    def __init__(self, message: str = "Ошибка внешнего сервиса", status_code: int = 503):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)