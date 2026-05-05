"""
Модель списков сравнения товаров.
Пользователь может создавать несколько списков сравнения.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, DateTime, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product


# Association table for many-to-many: ComparisonList <-> Product
comparison_items = Table(
    "comparison_items",
    Base.metadata,
    Column("comparison_list_id", Integer, ForeignKey("comparison_lists.id", ondelete="CASCADE"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("added_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False)
)


class ComparisonList(Base, TimestampMixin):
    """Список сравнения товаров.
    
    Поля:
        id: Уникальный идентификатор
        user_id: ID пользователя-владельца
        name: Название списка (например "Ноутбуки для работы")
        description: Описание списка
        max_items: Максимальное количество товаров (по умолчанию 4)
        is_active: Активен ли список
        
    Связь many-to-many с Product через comparison_items.
    """
    
    __tablename__ = "comparison_lists"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Owner
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID владельца"
    )
    
    # Info
    name: Mapped[str] = mapped_column(
        String(255),
        default="Сравнение",
        nullable=False,
        comment="Название списка"
    )
    description: Mapped[Optional[str]] = mapped_column(
        nullable=True,
        comment="Описание списка"
    )
    
    # Settings
    max_items: Mapped[int] = mapped_column(
        Integer,
        default=4,
        nullable=False,
        comment="Максимум товаров для сравнения"
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Активен ли список"
    )
    
    # Timestamps
    last_viewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата последнего просмотра"
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="comparison_lists")
    products: Mapped[List["Product"]] = relationship(
        "Product",
        secondary=comparison_items,
        back_populates="comparison_lists",
        order_by="comparison_items.c.added_at"
    )
    
    def __repr__(self) -> str:
        return f"<ComparisonList(id={self.id}, user={self.user_id}, items={len(self.products)})>"
    
    def can_add_product(self) -> bool:
        """Можно ли добавить ещё один товар."""
        return len(self.products) < self.max_items
    
    def has_product(self, product_id: int) -> bool:
        """Проверяет, есть ли товар в списке."""
        return any(p.id == product_id for p in self.products)
