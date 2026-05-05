"""
Модель товара - центральная сущность агрегатора.
Содержит основную информацию о товаре, цены хранятся отдельно (ProductPrice).
"""

import json
from typing import TYPE_CHECKING, List, Optional, Dict, Any

from sqlalchemy import String, Text, Float, Boolean, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.product_price import ProductPrice
    from app.models.favorite import Favorite
    from app.models.cart_item import CartItem
    from app.models.order_item import OrderItem
    from app.models.view_history import ViewHistory
    from app.models.comparison_list import ComparisonList
    from app.models.review import Review


class Product(Base, TimestampMixin):
    """Товар в агрегаторе.
    
    Поля:
        id: Уникальный идентификатор
        category_id: Категория товара
        name: Название товара
        slug: URL-friendly идентификатор
        description: Полное описание
        brand: Бренд производителя
        images: JSON массив URL изображений
        specifications: JSON характеристики
        rating: Средний рейтинг (0-5)
        review_count: Количество отзывов
        is_active: Активен ли товар
        views_count: Счётчик просмотров
    """
    
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Category relationship
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID категории"
    )
    
    # Basic info
    name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Название товара"
    )
    slug: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        index=True,
        nullable=False,
        comment="URL-friendly идентификатор"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Полное описание товара"
    )
    
    # Product details
    brand: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Бренд производителя"
    )
    sku: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Артикул/SKU"
    )
    
    # Media (JSON array of image URLs)
    images: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Массив URL изображений"
    )
    
    # Specifications (JSON key-value)
    specifications: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Технические характеристики"
    )
    
    # Ratings
    rating: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        comment="Средний рейтинг (0-5)"
    )
    review_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Количество отзывов"
    )
    
    # Status & Stats
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Активен ли товар"
    )
    views_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Счётчик просмотров"
    )
    
    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    prices: Mapped[List["ProductPrice"]] = relationship(
        "ProductPrice",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="product")
    cart_items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="product")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")
    view_history: Mapped[List["ViewHistory"]] = relationship("ViewHistory", back_populates="product")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="product")
    
    # Comparison lists (many-to-many through association table)
    comparison_lists: Mapped[List["ComparisonList"]] = relationship(
        "ComparisonList",
        secondary="comparison_items",
        back_populates="products"
    )
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name[:50]}..., slug={self.slug})>"
    
    @property
    def min_price(self) -> Optional[float]:
        """Минимальная цена среди всех маркетплейсов."""
        available_prices = [p.price for p in self.prices if p.is_available and p.price > 0]
        return min(available_prices) if available_prices else None
    
    @property
    def max_price(self) -> Optional[float]:
        """Максимальная цена среди всех маркетплейсов."""
        available_prices = [p.price for p in self.prices if p.is_available and p.price > 0]
        return max(available_prices) if available_prices else None
    
    @property
    def best_price(self) -> Optional["ProductPrice"]:
        """Лучшее предложение (минимальная цена)."""
        available = [p for p in self.prices if p.is_available and p.price > 0]
        return min(available, key=lambda x: x.price) if available else None
    
    def get_specifications_list(self) -> List[Dict[str, str]]:
        """Преобразует specifications в список для отображения."""
        if not self.specifications:
            return []
        return [{"name": k, "value": v} for k, v in self.specifications.items()]
