"""
API роуты для поиска товаров с автодополнением.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_optional_user
from app.models.product import Product
from app.models.category import Category
from app.models.marketplace import Marketplace
from app.models.user import User
from app.schemas.search import (
    SearchQuery,
    SearchResponse,
    AutocompleteResponse,
    SearchSuggestion,
    FacetCount,
    SearchFacets,
)
from app.schemas.product import ProductListItem

router = APIRouter()


def product_to_list_item(product: Product) -> dict:
    """Конвертирует Product в словарь."""
    prices_count = len([p for p in product.prices if p.is_available])
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "brand": product.brand,
        "images": product.images or [],
        "rating": product.rating,
        "review_count": product.review_count,
        "min_price": product.min_price,
        "max_price": product.max_price,
        "prices_count": prices_count,
    }


@router.get("/", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., min_length=1, max_length=200, description="Поисковый запрос"),
    category_id: Optional[int] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    marketplace_id: Optional[int] = None,
    in_stock: Optional[bool] = None,
    sort_by: str = Query("relevance", enum=["relevance", "price_asc", "price_desc", "rating", "newest"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Продвинутый поиск товаров с фильтрами и фасетами.
    
    - **q**: Поисковый запрос (по названию, описанию, бренду)
    - **category_id**: Фильтр по категории
    - **brand**: Фильтр по бренду
    - **min_price/max_price**: Диапазон цен
    - **min_rating**: Минимальный рейтинг
    - **sort_by**: Сортировка
    """
    # Базовый запрос
    query = select(Product).where(Product.is_active == True)
    
    # Поисковый запрос (по названию, описанию, бренду, SKU)
    search_filter = or_(
        Product.name.ilike(f"%{q}%"),
        Product.description.ilike(f"%{q}%"),
        Product.brand.ilike(f"%{q}%"),
        Product.sku.ilike(f"%{q}%"),
    )
    query = query.where(search_filter)
    
    # Применяем фильтры
    if category_id:
        query = query.where(Product.category_id == category_id)
    if brand:
        query = query.where(Product.brand.ilike(f"%{brand}%"))
    if min_rating is not None:
        query = query.where(Product.rating >= min_rating)
    
    # Подгружаем связанные данные
    query = query.options(
        selectinload(Product.prices),
        selectinload(Product.category)
    )
    
    # Подсчёт общего количества для пагинации
    count_query = select(func.count(Product.id)).where(
        and_(Product.is_active == True, search_filter)
    )
    if category_id:
        count_query = count_query.where(Product.category_id == category_id)
    
    result = await db.execute(count_query)
    total = result.scalar() or 0
    
    # Сортировка
    if sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    elif sort_by == "rating":
        query = query.order_by(Product.rating.desc())
    elif sort_by == "price_asc":
        # Упрощённая сортировка
        query = query.order_by(Product.id)
    elif sort_by == "price_desc":
        query = query.order_by(Product.id.desc())
    else:  # relevance
        query = query.order_by(
            # Сначала точные совпадения в названии
            (Product.name.ilike(f"{q}%")).desc(),
            Product.rating.desc(),
            Product.views_count.desc(),
        )
    
    # Пагинация
    skip = (page - 1) * page_size
    query = query.offset(skip).limit(page_size)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    # Конвертируем в схемы
    items = [product_to_list_item(p) for p in products]
    
    # Фильтруем по цене если указана
    if min_price is not None or max_price is not None:
        filtered_items = []
        for item in items:
            item_min_price = item.get("min_price")
            if item_min_price is not None:
                if min_price is not None and item_min_price < min_price:
                    continue
                if max_price is not None and item_min_price > max_price:
                    continue
            filtered_items.append(item)
        items = filtered_items
        total = len(items)
    
    # Собираем фасеты (доступные фильтры)
    facets = await build_facets(db, q, category_id)
    
    return {
        "query": q,
        "corrected_query": None,  # В будущем: исправление опечаток
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size if page_size > 0 else 1,
        "items": items,
        "facets": facets,
    }


async def build_facets(
    db: AsyncSession,
    query: str,
    current_category_id: Optional[int] = None
) -> SearchFacets:
    """Строит фасеты (агрегированные фильтры) для результатов поиска."""
    
    # Фасет по категориям
    category_query = (
        select(Category.id, Category.name, func.count(Product.id))
        .join(Product, Product.category_id == Category.id)
        .where(
            and_(
                Product.is_active == True,
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%"),
                    Product.brand.ilike(f"%{query}%"),
                )
            )
        )
        .group_by(Category.id, Category.name)
    )
    result = await db.execute(category_query)
    category_facets = [
        FacetCount(value=str(row[0]), label=row[1], count=row[2], 
                  selected=current_category_id == row[0])
        for row in result.all()
    ]
    
    # Фасет по брендам
    brand_query = (
        select(Product.brand, func.count(Product.id))
        .where(
            and_(
                Product.is_active == True,
                Product.brand.isnot(None),
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%"),
                    Product.brand.ilike(f"%{query}%"),
                )
            )
        )
        .group_by(Product.brand)
    )
    if current_category_id:
        brand_query = brand_query.where(Product.category_id == current_category_id)
    
    result = await db.execute(brand_query)
    brand_facets = [
        FacetCount(value=row[0], label=row[0], count=row[1], selected=False)
        for row in result.all() if row[0]
    ]
    
    # Фасет по маркетплейсам
    mp_query = (
        select(Marketplace.id, Marketplace.name, func.count(Product.id))
        .join(ProductPrice, ProductPrice.marketplace_id == Marketplace.id)
        .join(Product, Product.id == ProductPrice.product_id)
        .where(
            and_(
                Product.is_active == True,
                ProductPrice.is_available == True,
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%"),
                    Product.brand.ilike(f"%{query}%"),
                )
            )
        )
        .group_by(Marketplace.id, Marketplace.name)
    )
    result = await db.execute(mp_query)
    mp_facets = [
        FacetCount(value=str(row[0]), label=row[1], count=row[2], selected=False)
        for row in result.all()
    ]
    
    return SearchFacets(
        categories=category_facets,
        brands=brand_facets[:20],  # Ограничиваем количество
        price_ranges=[
            {"label": "До $50", "min": 0, "max": 50},
            {"label": "$50 - $100", "min": 50, "max": 100},
            {"label": "$100 - $500", "min": 100, "max": 500},
            {"label": "$500+", "min": 500, "max": None},
        ],
        marketplaces=mp_facets,
    )


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    Автодополнение поисковых запросов.
    
    Возвращает:
    - Совпадающие товары
    - Категории
    - Популярные бренды
    """
    suggestions: List[SearchSuggestion] = []
    
    # Поиск товаров (названия)
    product_query = (
        select(Product.name, Product.slug, Product.brand)
        .where(
            and_(
                Product.is_active == True,
                Product.name.ilike(f"%{q}%"),
            )
        )
        .limit(limit)
    )
    result = await db.execute(product_query)
    
    for row in result.all():
        name, slug, brand = row
        # Подсвечиваем совпадение
        highlighted = name.replace(q, f"<b>{q}</b>")
        suggestions.append(SearchSuggestion(
            text=name,
            type="product",
            highlight=highlighted,
            url=f"/product/{slug}",
        ))
    
    # Поиск категорий
    if len(suggestions) < limit:
        remaining = limit - len(suggestions)
        category_query = (
            select(Category.name, Category.slug)
            .where(
                and_(
                    Category.is_active == True,
                    Category.name.ilike(f"%{q}%"),
                )
            )
            .limit(remaining)
        )
        result = await db.execute(category_query)
        
        for row in result.all():
            name, slug = row
            highlighted = name.replace(q, f"<b>{q}</b>")
            suggestions.append(SearchSuggestion(
                text=name,
                type="category",
                highlight=highlighted,
                url=f"/category/{slug}",
            ))
    
    # Популярные бренды (совпадающие с запросом)
    brand_query = (
        select(Product.brand, func.count(Product.id))
        .where(
            and_(
                Product.is_active == True,
                Product.brand.isnot(None),
                Product.brand.ilike(f"%{q}%"),
            )
        )
        .group_by(Product.brand)
        .order_by(func.count(Product.id).desc())
        .limit(5)
    )
    result = await db.execute(brand_query)
    brands = [row[0] for row in result.all()]
    
    # Категории с результатами
    category_result_query = (
        select(Category.id, Category.name, func.count(Product.id))
        .join(Product, Product.category_id == Category.id)
        .where(
            and_(
                Product.is_active == True,
                or_(
                    Product.name.ilike(f"%{q}%"),
                    Product.description.ilike(f"%{q}%"),
                )
            )
        )
        .group_by(Category.id, Category.name)
        .limit(5)
    )
    result = await db.execute(category_result_query)
    categories = [
        {"id": row[0], "name": row[1], "count": row[2]}
        for row in result.all()
    ]
    
    return AutocompleteResponse(
        query=q,
        suggestions=suggestions,
        categories=categories,
        brands=brands,
    )


@router.get("/popular")
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=20),
):
    """
    Получение популярных поисковых запросов.
    
    В реальном приложении здесь был бы запрос к аналитике.
    """
    # Популярные запросы (заглушка)
    popular = [
        {"query": "iPhone 15", "count": 15420},
        {"query": "Samsung Galaxy", "count": 12350},
        {"query": "ноутбук", "count": 9870},
        {"query": "наушники", "count": 8650},
        {"query": "PlayStation 5", "count": 7430},
        {"query": "Xiaomi", "count": 6890},
        {"query": "AirPods", "count": 6120},
        {"query": "часы Apple Watch", "count": 5980},
        {"query": "планшет", "count": 4560},
        {"query": "фотоаппарат", "count": 3890},
    ]
    
    return {"queries": popular[:limit]}
