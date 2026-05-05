"""
Pydantic схемы для категорий товаров.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


# =============================================================================
# Base Schemas
# =============================================================================

class CategoryBase(BaseModel):
    """Базовая схема категории."""
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None


# =============================================================================
# Request Schemas
# =============================================================================

class CategoryCreate(CategoryBase):
    """Схема создания категории."""
    parent_id: Optional[int] = None
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdate(BaseModel):
    """Схема обновления категории."""
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# =============================================================================
# Response Schemas
# =============================================================================

class CategoryResponse(CategoryBase):
    """Схема ответа с категорией."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    parent_id: Optional[int] = None
    level: int
    sort_order: int
    is_active: bool
    created_at: datetime


class CategoryTree(CategoryResponse):
    """Схема категории с вложенными подкатегориями."""
    children: List["CategoryTree"] = []


class CategoryListResponse(BaseModel):
    """Схема списка категорий."""
    items: List[CategoryResponse]
    total: int


class CategoryWithPath(CategoryResponse):
    """Категория с полным путём (breadcrumb)."""
    path: List[dict] = []  # [{id, name, slug}, ...]
