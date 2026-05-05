"""
Pydantic схемы для товаров.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.marketplace import MarketplaceSimple


# =============================================================================
# Product Price Schemas
# =============================================================================

class ProductPriceInfo(BaseModel):
    """Информация о цене на маркетплейсе."""
    model_config = ConfigDict(from_attributes=True)
    
    marketplace: MarketplaceSimple
    price: float
    original_price: Optional[float] = None
    discount_percent: Optional[float] = None
    currency: str
    product_url: str
    is_available: bool
    availability: str
    delivery_range: Optional[str] = None
    delivery_country: Optional[str] = None
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None


class PriceCreate(BaseModel):
    """Схема создания цены товара."""
    marketplace_id: int
    price: float = Field(..., gt=0)
    original_price: Optional[float] = None
    currency: str = "USD"
    product_url: str
    external_id: Optional[str] = None
    availability: str = "in_stock"
    delivery_days_min: Optional[int] = None
    delivery_days_max: Optional[int] = None
    delivery_country: Optional[str] = None
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None


# =============================================================================
# Product Schemas
# =============================================================================

class ProductBase(BaseModel):
    """Базовая схема товара."""
    name: str
    slug: str
    description: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None


class ProductCreate(ProductBase):
    """Схема создания товара."""
    category_id: int
    images: List[str] = []
    specifications: Dict[str, Any] = {}
    prices: List[PriceCreate] = []


class ProductUpdate(BaseModel):
    """Схема обновления товара."""
    name: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    images: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


# =============================================================================
# Response Schemas
# =============================================================================

class ProductListItem(BaseModel):
    """Упрощённая схема товара для списка."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    slug: str
    brand: Optional[str] = None
    images: List[str]
    rating: float
    review_count: int
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    prices_count: int = 0


class ProductResponse(ProductBase):
    """Полная схема товара."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    category_id: int
    category_name: str
    images: List[str]
    specifications: Dict[str, Any]
    rating: float
    review_count: int
    views_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Aggregated prices
    prices: List[ProductPriceInfo]
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    best_price: Optional[ProductPriceInfo] = None


class ProductListResponse(BaseModel):
    """Схема списка товаров с пагинацией."""
    items: List[ProductListItem]
    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# Filter Schemas
# =============================================================================

class ProductFilter(BaseModel):
    """Схема фильтров для поиска товаров."""
    category_id: Optional[int] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    marketplace_id: Optional[int] = None
    in_stock: Optional[bool] = None
    sort_by: str = "relevance"  # relevance, price_asc, price_desc, rating, newest


class PriceRange(BaseModel):
    """Диапазон цен для фильтра."""
    min: float
    max: float


class ProductFiltersResponse(BaseModel):
    """Доступные фильтры для категории/поиска."""
    categories: List[dict] = []
    brands: List[str] = []
    price_range: PriceRange
    marketplaces: List[MarketplaceSimple] = []
