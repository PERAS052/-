"""
Кастомные исключения для приложения.
Используются для единообразной обработки ошибок.
"""

from typing import Optional, Dict, Any


class AggregatorException(Exception):
    """Базовое исключение приложения."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AggregatorException):
    """Ошибка аутентификации (401 Unauthorized)."""
    
    def __init__(self, message: str = "Ошибка аутентификации"):
        super().__init__(message, status_code=401)


class AuthorizationError(AggregatorException):
    """Ошибка авторизации (403 Forbidden)."""
    
    def __init__(self, message: str = "Доступ запрещён"):
        super().__init__(message, status_code=403)


class NotFoundError(AggregatorException):
    """Ресурс не найден (404 Not Found)."""
    
    def __init__(self, resource: str = "Ресурс", identifier: str = ""):
        message = f"{resource} не найден"
        if identifier:
            message += f" ({identifier})"
        super().__init__(message, status_code=404)


class ValidationError(AggregatorException):
    """Ошибка валидации данных (422 Unprocessable Entity)."""
    
    def __init__(
        self,
        message: str = "Ошибка валидации",
        errors: Optional[Dict[str, str]] = None
    ):
        super().__init__(message, status_code=422, details=errors or {})


class ConflictError(AggregatorException):
    """Конфликт данных (409 Conflict)."""
    
    def __init__(self, message: str = "Конфликт данных"):
        super().__init__(message, status_code=409)


class RateLimitError(AggregatorException):
    """Превышен лимит запросов (429 Too Many Requests)."""
    
    def __init__(self, message: str = "Слишком много запросов"):
        super().__init__(message, status_code=429)
