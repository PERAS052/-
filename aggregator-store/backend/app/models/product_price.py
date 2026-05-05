"""
Модель цен товара на разных маркетплейсах.
Отдельная таблица для хранения истории цен и текущих предложений.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.marketplace import Marketplace


class ProductPrice(Base):
    """Цена товара на конкретном маркетплейсе.
    
    Поля:
        id: Уникальный идентификатор
        product_id: Ссылка на товар
        marketplace_id: Ссылка на маркетплейс
        price: Текущая цена
        original_price: Цена без скидки (для отображения скидки)
        currency: Валюта цены
        product_url: Прямая ссылка на товар
        availability: Наличие (в наличии, под заказ, нет)
        is_available: Доступен ли товар для покупки
        delivery_days: Срок доставки в днях
        delivery_country: Страна доставки
        seller_name: Название продавца
        rating: Рейтинг продавца
        updated_at: Дата последнего обновления цены
    """
    
    __tablename__ = "product_prices"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign Keys
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID товара"
    )
    marketplace_id: Mapped[int] = mapped_column(
        ForeignKey("marketplaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID маркетплейса"
    )
    
    # Pricing
    price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Текущая цена"
    )
    original_price: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Цена без скидки"
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
        comment="Валюта (ISO 4217)"
    )
    
    # Marketplace details
    product_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        comment="Прямая ссылка на товар"
    )
    external_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="ID товара в системе маркетплейса"
    )
    
    # Availability
    availability: Mapped[str] = mapped_column(
        String(50),
        default="in_stock",
        nullable=False,
        comment="Статус: in_stock, out_of_stock, pre_order"
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Доступен ли для покупки"
    )
    
    # Delivery
    delivery_days_min: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Минимальный срок доставки (дни)"
    )
    delivery_days_max: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Максимальный срок доставки (дни)"
    )
    delivery_country: Mapped[Optional[str]] = mapped_column(
        String(2),
        nullable=True,
        comment="Страна доставки (ISO 3166-1 alpha-2)"
    )
    
    # Seller info
    seller_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Название продавца"
    )
    seller_rating: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Рейтинг продавца (0-5)"
    )
    
    # Update tracking
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Дата последнего обновления цены"
    )
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="prices")
    marketplace: Mapped["Marketplace"] = relationship("Marketplace", back_populates="product_prices")
    
    def __repr__(self) -> str:
        return f"<ProductPrice(id={self.id}, product={self.product_id}, {self.price} {self.currency})>"
    
    @property
    def discount_percent(self) -> Optional[float]:
        """Процент скидки (если есть)."""
        if self.original_price and self.original_price > self.price:
            return round((1 - self.price / self.original_price) * 100, 1)
        return None
    
    @property
    def delivery_range(self) -> str:
        """Диапазон доставки для отображения."""
        if self.delivery_days_min and self.delivery_days_max:
            if self.delivery_days_min == self.delivery_days_max:
                return f"{self.delivery_days_min} дн."
            return f"{self.delivery_days_min}-{self.delivery_days_max} дн."
        elif self.delivery_days_min:
            return f"от {self.delivery_days_min} дн."
        elif self.delivery_days_max:
            return f"до {self.delivery_days_max} дн."
        return "Н/Д"
