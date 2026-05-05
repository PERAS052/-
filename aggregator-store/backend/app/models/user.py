"""
Модель пользователя с поддержкой 3 ролей:
- client: обычный покупатель
- manager: менеджер магазина
- admin: администратор системы
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Boolean, Enum, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.favorite import Favorite
    from app.models.cart_item import CartItem
    from app.models.order import Order
    from app.models.view_history import ViewHistory
    from app.models.comparison_list import ComparisonList
    from app.models.review import Review


class UserRole(str, enum.Enum):
    """Перечисление ролей пользователей."""
    CLIENT = "client"      # Обычный покупатель
    MANAGER = "manager"      # Менеджер (управление товарами)
    ADMIN = "admin"          # Администратор (полный доступ)


class User(Base, TimestampMixin):
    """Модель пользователя системы.
    
    Поля:
        id: UUID идентификатор
        email: Уникальный email
        password_hash: Хеш пароля (bcrypt)
        role: Роль пользователя (client/manager/admin)
        full_name: Полное имя
        phone: Телефон
        avatar_url: URL аватарки
        is_active: Активен ли аккаунт
        email_verified: Подтверждён ли email
        last_login: Дата последнего входа
    """
    
    __tablename__ = "users"
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="Email пользователя (уникальный)"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Хеш пароля (bcrypt)"
    )
    
    # Role & Profile
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.CLIENT,
        nullable=False,
        comment="Роль: client, manager, admin"
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Полное имя пользователя"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Номер телефона"
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL аватарки"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Активен ли аккаунт"
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Подтверждён ли email"
    )
    
    # Timestamps
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата последнего входа"
    )
    
    # Relationships
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="user"
    )
    view_history: Mapped[List["ViewHistory"]] = relationship(
        "ViewHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    comparison_lists: Mapped[List["ComparisonList"]] = relationship(
        "ComparisonList",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review",
        back_populates="user"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
    
    @property
    def is_admin(self) -> bool:
        """Проверка на администратора."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_manager(self) -> bool:
        """Проверка на менеджера."""
        return self.role in (UserRole.MANAGER, UserRole.ADMIN)
