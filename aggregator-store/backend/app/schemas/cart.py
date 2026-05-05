"""
Pydantic схемы для корзины.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.product import ProductListItem


# =============================================================================
# Request Schemas
# =============================================================================

class CartItemCreate(BaseModel):
    """Схема добавления товара в корзину."""
    product_id: int
    marketplace_id: int
    quantity: int = Field(..., ge=1, le=99)


class CartItemUpdate(BaseModel):
    """Схема обновления количества."""
    quantity: int = Field(..., ge=1, le=99)


# =============================================================================
# Response Schemas
# =============================================================================

class CartItemMarketplaceInfo(BaseModel):
    """Информация о маркетплейсе в корзине."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    code: str
    logo_url: str
    currency: str


class CartItemProductInfo(BaseModel):
    """Информация о товаре в корзине."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    slug: str
    brand: Optional[str]
    image: str  # First image
    rating: float


class CartItemPriceInfo(BaseModel):
    """Информация о цене на момент добавления."""
    model_config = ConfigDict(from_attributes=True)
    
    price: float
    original_price: Optional[float]
    discount_percent: Optional[float]
    currency: str
    is_available: bool
    product_url: str


class CartItemResponse(BaseModel):
    """Элемент корзины в ответе."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product: CartItemProductInfo
    marketplace: CartItemMarketplaceInfo
    price_info: CartItemPriceInfo
    quantity: int
    subtotal: float
    added_at: datetime


class CartSummary(BaseModel):
    """Сводка по корзине."""
    total_items: int
    unique_items: int
    subtotal: float
    currency: str = "USD"
    # delivery_estimate: Optional[str] = None


class CartResponse(BaseModel):
    """Полный ответ корзины."""
    items: List[CartItemResponse]
    summary: CartSummary
