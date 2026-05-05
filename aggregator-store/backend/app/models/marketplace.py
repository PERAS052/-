"""
Модель маркетплейсов (AliExpress, Amazon, Wildberries и т.д.).
Каждый товар может иметь цены из разных маркетплейсов.
"""

from typing import TYPE_CHECKING, List

from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.product_price import ProductPrice


class Marketplace(Base, TimestampMixin):
    """Маркетплейс - источник товаров и цен.
    
    Поля:
        id: Уникальный идентификатор
        name: Название маркетплейса
        code: Короткий код (aliexpress, amazon, ozon, wildberries)
        logo_url: Логотип маркетплейса
        website_url: Основной сайт
        api_endpoint: API endpoint (если есть)
        currency: Валюта по умолчанию
        country: Страна базирования
        description: Описание
        is_active: Активен ли маркетплейс
        parsing_enabled: Включён ли парсинг
    """
    
    __tablename__ = "marketplaces"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Basic info
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Название маркетплейса"
    )
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="Код: aliexpress, amazon, ozon, wildberries, yandex_market"
    )
    
    # Media
    logo_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="URL логотипа"
    )
    website_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="URL основного сайта"
    )
    
    # API/Integration
    api_endpoint: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="API endpoint (опционально)"
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
        comment="Валюта по умолчанию (ISO 4217)"
    )
    country: Mapped[str] = mapped_column(
        String(2),
        default="US",
        nullable=False,
        comment="Страна (ISO 3166-1 alpha-2)"
    )
    
    # Description
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Описание маркетплейса"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Активен ли маркетплейс"
    )
    parsing_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Включён ли парсинг/обновление цен"
    )
    
    # Relationships
    product_prices: Mapped[List["ProductPrice"]] = relationship(
        "ProductPrice",
        back_populates="marketplace"
    )
    
    def __repr__(self) -> str:
        return f"<Marketplace(id={self.id}, name={self.name}, code={self.code})>"
