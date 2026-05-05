"""
API роуты для товаров.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, require_manager, get_current_user, get_optional_user
from app.models.product import Product
from app.models.product_price import ProductPrice
from app.models.category import Category
from app.models.marketplace import Marketplace
from app.models.user import User
from app.models.view_history import ViewHistory
from app.schemas.product import (
    ProductResponse,
    ProductListItem,
    ProductListResponse,
    ProductCreate,
    ProductUpdate,
    ProductFilter,
    PriceCreate,
    ProductFiltersResponse,
    PriceRange,
)

router = APIRouter()


def product_to_list_item(product: Product) -> dict:
    """Конвертирует Product в ProductListItem."""
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


def product_to_response(product: Product) -> dict:
    """Конвертирует Product в ProductResponse."""
    prices_info = []
    for price in product.prices:
        if price.marketplace:
            prices_info.append({
                "marketplace": {
                    "id": price.marketplace.id,
                    "name": price.marketplace.name,
                    "code": price.marketplace.code,
                    "logo_url": price.marketplace.logo_url,
                },
                "price": price.price,
                "original_price": price.original_price,
                "discount_percent": price.discount_percent,
                "currency": price.currency,
                "product_url": price.product_url,
                "is_available": price.is_available,
                "availability": price.availability,
                "delivery_range": price.delivery_range,
                "delivery_country": price.delivery_country,
                "seller_name": price.seller_name,
                "seller_rating": price.seller_rating,
            })
    
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "brand": product.brand,
        "sku": product.sku,
        "category_id": product.category_id,
        "category_name": product.category.name if product.category else None,
        "images": product.images or [],
        "specifications": product.specifications or {},
        "rating": product.rating,
        "review_count": product.review_count,
        "views_count": product.views_count,
        "is_active": product.is_active,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "prices": prices_info,
        "min_price": product.min_price,
        "max_price": product.max_price,
        "best_price": next(
            (p for p in prices_info if p["is_available"]), 
            None
        ),
    }


@router.get("/", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    sort_by: str = Query("newest", enum=["newest", "price_asc", "price_desc", "rating", "popular"]),
    db: AsyncSession = Depends(get_db),
):
    """
    Список товаров с фильтрами и сортировкой.
    """
    # Базовый запрос
    query = select(Product).where(Product.is_active == True)
    
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
    
    # Считаем общее количество
    count_query = select(func.count(Product.id)).where(Product.is_active == True)
    if category_id:
        count_query = count_query.where(Product.category_id == category_id)
    
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Сортировка
    if sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    elif sort_by == "price_asc":
        # Сложная сортировка по минимальной цене требует подзапроса
        query = query.order_by(Product.id)  # Упрощённая версия
    elif sort_by == "price_desc":
        query = query.order_by(Product.id.desc())
    elif sort_by == "rating":
        query = query.order_by(Product.rating.desc())
    elif sort_by == "popular":
        query = query.order_by(Product.views_count.desc())
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    # Конвертируем в схемы
    items = [product_to_list_item(p) for p in products]
    
    # Фильтруем по цене если указана
    if min_price is not None or max_price is not None:
        filtered_items = []
        for item in items:
            min_p = item.get("min_price")
            if min_p is not None:
                if min_price is not None and min_p < min_price:
                    continue
                if max_price is not None and min_p > max_price:
                    continue
            filtered_items.append(item)
        items = filtered_items
        total = len(items)
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 1,
    }


@router.get("/{slug}", response_model=ProductResponse)
async def get_product(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Получение детальной информации о товаре.
    
    - Записывает просмотр в историю (для авторизованных)
    - Увеличивает счётчик просмотров
    """
    result = await db.execute(
        select(Product)
        .where(Product.slug == slug)
        .options(
            selectinload(Product.prices).selectinload(ProductPrice.marketplace),
            selectinload(Product.category)
        )
    )
    product = result.scalar_one_or_none()
    
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    # Увеличиваем счётчик просмотров
    product.views_count += 1
    
    # Записываем в историю просмотров для авторизованных
    if current_user:
        # Проверяем существование записи
        result = await db.execute(
            select(ViewHistory).where(
                and_(
                    ViewHistory.user_id == current_user.id,
                    ViewHistory.product_id == product.id
                )
            )
        )
        view = result.scalar_one_or_none()
        
        from datetime import datetime
        if view:
            view.view_count += 1
            view.viewed_at = datetime.utcnow()
        else:
            view = ViewHistory(
                user_id=current_user.id,
                product_id=product.id,
                viewed_at=datetime.utcnow(),
            )
            db.add(view)
    
    await db.commit()
    
    return product_to_response(product)


@router.get("/{product_id}/similar")
async def get_similar_products(
    product_id: int,
    limit: int = Query(8, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение похожих товаров (по категории и бренду).
    """
    # Получаем товар
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    # Ищем похожие в той же категории
    query = (
        select(Product)
        .where(
            and_(
                Product.id != product_id,
                Product.category_id == product.category_id,
                Product.is_active == True,
            )
        )
        .options(selectinload(Product.prices))
        .order_by(Product.rating.desc(), Product.views_count.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    similar = result.scalars().all()
    
    return {
        "items": [product_to_list_item(p) for p in similar],
        "total": len(similar),
    }


# =============================================================================
# Admin endpoints
# =============================================================================

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание товара (только для менеджеров).
    """
    # Проверяем категорию
    result = await db.execute(
        select(Category).where(Category.id == product_data.category_id)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория не найдена"
        )
    
    # Проверяем уникальность slug
    result = await db.execute(
        select(Product).where(Product.slug == product_data.slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Товар с таким slug уже существует"
        )
    
    # Создаём товар
    new_product = Product(
        name=product_data.name,
        slug=product_data.slug,
        description=product_data.description,
        category_id=product_data.category_id,
        brand=product_data.brand,
        sku=product_data.sku,
        images=product_data.images or [],
        specifications=product_data.specifications or {},
    )
    
    db.add(new_product)
    await db.flush()  # Получаем ID
    
    # Создаём цены
    for price_data in product_data.prices:
        # Проверяем маркетплейс
        result = await db.execute(
            select(Marketplace).where(Marketplace.id == price_data.marketplace_id)
        )
        marketplace = result.scalar_one_or_none()
        
        if not marketplace:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Маркетплейс с ID {price_data.marketplace_id} не найден"
            )
        
        price = ProductPrice(
            product_id=new_product.id,
            marketplace_id=price_data.marketplace_id,
            price=price_data.price,
            original_price=price_data.original_price,
            currency=price_data.currency,
            product_url=price_data.product_url,
            external_id=price_data.external_id,
            availability=price_data.availability,
            delivery_days_min=price_data.delivery_days_min,
            delivery_days_max=price_data.delivery_days_max,
            delivery_country=price_data.delivery_country,
            seller_name=price_data.seller_name,
            seller_rating=price_data.seller_rating,
        )
        db.add(price)
    
    await db.commit()
    await db.refresh(new_product)
    
    return product_to_response(new_product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновление товара.
    """
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.prices).selectinload(ProductPrice.marketplace))
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    # Обновляем поля
    if product_update.name is not None:
        product.name = product_update.name
    if product_update.description is not None:
        product.description = product_update.description
    if product_update.brand is not None:
        product.brand = product_update.brand
    if product_update.sku is not None:
        product.sku = product_update.sku
    if product_update.images is not None:
        product.images = product_update.images
    if product_update.specifications is not None:
        product.specifications = product_update.specifications
    if product_update.is_active is not None:
        product.is_active = product_update.is_active
    
    # Проверяем slug
    if product_update.slug and product_update.slug != product.slug:
        result = await db.execute(
            select(Product).where(Product.slug == product_update.slug)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Товар с таким slug уже существует"
            )
        product.slug = product_update.slug
    
    await db.commit()
    await db.refresh(product)
    
    return product_to_response(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Удаление товара (soft delete).
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    product.is_active = False
    await db.commit()
    
    return None
