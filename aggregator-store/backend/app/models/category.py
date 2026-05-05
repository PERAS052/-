"""
Модель категорий товаров с поддержкой иерархии (дерево).
Использует паттерн Adjacency List для родительских категорий.
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product


class Category(Base, TimestampMixin):
    """Категория товаров с поддержкой подкатегорий.
    
    Поля:
        id: Уникальный идентификатор
        name: Название категории
        slug: URL-friendly идентификатор
        description: Описание категории
        image_url: Изображение категории
        parent_id: ID родительской категории (для подкатегорий)
        level: Уровень вложенности (0 - корневые)
        sort_order: Порядок сортировки
        is_active: Активна ли категория
    """
    
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Basic info
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Название категории"
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="URL-friendly идентификатор"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Описание категории"
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL изображения категории"
    )
    
    # Hierarchy
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="ID родительской категории"
    )
    level: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Уровень вложенности (0 - корень)"
    )
    
    # Settings
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Порядок сортировки"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Активна ли категория"
    )
    
    # Relationships
    parent: Mapped[Optional["Category"]] = relationship(
        "Category",
        remote_side=[id],
        back_populates="children"
    )
    children: Mapped[List["Category"]] = relationship(
        "Category",
        back_populates="parent"
    )
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category"
    )
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name}, slug={self.slug})>"
    
    @property
    def full_path(self) -> str:
        """Возвращает полный путь категории (breadcrumb)."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
