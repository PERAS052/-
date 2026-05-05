"""
Pydantic схемы для пользователей и аутентификации.
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRole(str, Enum):
    """Роли пользователей."""
    CLIENT = "client"
    MANAGER = "manager"
    ADMIN = "admin"


# =============================================================================
# Base Schemas
# =============================================================================

class UserBase(BaseModel):
    """Базовая схема пользователя."""
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None


# =============================================================================
# Request Schemas
# =============================================================================

class UserCreate(UserBase):
    """Схема регистрации пользователя."""
    password: str = Field(..., min_length=8, max_length=100, description="Пароль минимум 8 символов")
    role: UserRole = UserRole.CLIENT


class UserLogin(BaseModel):
    """Схема входа в систему."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    """Схема обновления профиля."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    """Схема смены пароля."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# =============================================================================
# Response Schemas
# =============================================================================

class UserResponse(UserBase):
    """Схема ответа с данными пользователя."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    role: UserRole
    avatar_url: Optional[str] = None
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class Token(BaseModel):
    """Схема токенов аутентификации."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Время жизни access token в секундах")


class TokenPayload(BaseModel):
    """Схема payload JWT токена."""
    sub: Optional[int] = None  # user_id
    exp: Optional[datetime] = None
    type: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Схема запроса на обновление токена."""
    refresh_token: str
