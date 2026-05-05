"""
Pydantic схемы для поиска.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.product import ProductListItem


# =============================================================================
# Request Schemas
# =============================================================================

class SearchQuery(BaseModel):
    """Параметры поискового запроса."""
    q: str = Field(..., min_length=1, max_length=200, description="Поисковый запрос")
    category_id: Optional[int] = None
    brand: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    marketplace_id: Optional[int] = None
    in_stock: Optional[bool] = None
    sort_by: str = "relevance"  # relevance, price_asc, price_desc, rating, newest
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class AutocompleteQuery(BaseModel):
    """Параметры автодополнения."""
    q: str = Field(..., min_length=1, max_length=100)
    limit: int = Field(10, ge=1, le=20)


# =============================================================================
# Response Schemas
# =============================================================================

class SearchSuggestion(BaseModel):
    """Подсказка автодополнения."""
    text: str
    type: str  # "product", "category", "brand"
    highlight: Optional[str] = None  # HTML с выделением совпадения
    url: Optional[str] = None


class AutocompleteResponse(BaseModel):
    """Ответ автодополнения."""
    query: str
    suggestions: List[SearchSuggestion]
    categories: List[dict] = []  # [{"id": 1, "name": "Ноутбуки", "count": 42}]
    brands: List[str] = []


class FacetCount(BaseModel):
    """Количество для фасета."""
    value: str
    count: int
    selected: bool = False


class SearchFacets(BaseModel):
    """Фасеты для фильтрации результатов."""
    categories: List[FacetCount] = []
    brands: List[FacetCount] = []
    price_ranges: List[dict] = []
    marketplaces: List[FacetCount] = []


class SearchResponse(BaseModel):
    """Ответ поиска с результатами и фасетами."""
    query: str
    corrected_query: Optional[str] = None  # Исправленный запрос (если опечатка)
    total: int
    page: int
    page_size: int
    pages: int
    items: List[ProductListItem]
    facets: SearchFacets
    sort_options: List[dict] = [
        {"value": "relevance", "label": "По релевантности"},
        {"value": "price_asc", "label": "Сначала дешевле"},
        {"value": "price_desc", "label": "Сначала дороже"},
        {"value": "rating", "label": "По рейтингу"},
        {"value": "newest", "label": "Новинки"},
    ]


class PopularSearch(BaseModel):
    """Популярный поисковый запрос."""
    query: str
    count: int
