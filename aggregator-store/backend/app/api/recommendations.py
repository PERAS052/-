"""
API роуты для ML-рекомендаций.
"""

from typing import List, Optional
import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_optional_user, get_current_user
from app.models.product import Product
from app.models.view_history import ViewHistory
from app.models.favorite import Favorite
from app.models.category import Category
from app.models.user import User
from app.schemas.product import ProductListItem

router = APIRouter()


def product_to_list_item(product: Product) -> dict:
    """Конвертирует Product в списочный формат."""
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


@router.get("/for-you", response_model=List[ProductListItem])
async def get_personal_recommendations(
    limit: int = Query(10, ge=1, le=20),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Персональные рекомендации "Для вас".
    
    Алгоритм:
    1. Если пользователь авторизован - анализируем историю просмотров
    2. Ищем похожие товары из тех же категорий
    3. Если нет истории - возвращаем популярные товары
    """
    if current_user:
        # Получаем историю просмотров пользователя
        result = await db.execute(
            select(ViewHistory)
            .where(ViewHistory.user_id == current_user.id)
            .order_by(desc(ViewHistory.viewed_at))
            .limit(20)
        )
        view_history = result.scalars().all()
        
        if view_history:
            # Получаем ID категорий из истории просмотров
            product_ids = [v.product_id for v in view_history]
            
            result = await db.execute(
                select(Product.category_id)
                .where(Product.id.in_(product_ids))
                .distinct()
            )
            category_ids = [row[0] for row in result.all()]
            
            # Ищем товары из тех же категорий
            result = await db.execute(
                select(Product)
                .where(
                    and_(
                        Product.category_id.in_(category_ids),
                        Product.id.notin_(product_ids),  # Исключаем уже просмотренные
                        Product.is_active == True,
                    )
                )
                .options(selectinload(Product.prices))
                .order_by(desc(Product.rating), desc(Product.views_count))
                .limit(limit)
            )
            products = result.scalars().all()
            
            if products:
                return [product_to_list_item(p) for p in products]
    
    # Fallback: популярные товары
    result = await db.execute(
        select(Product)
        .where(Product.is_active == True)
        .options(selectinload(Product.prices))
        .order_by(desc(Product.views_count), desc(Product.rating))
        .limit(limit)
    )
    products = result.scalars().all()
    
    return [product_to_list_item(p) for p in products]


@router.get("/similar/{product_id}", response_model=List[ProductListItem])
async def get_similar_products(
    product_id: int,
    limit: int = Query(8, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    "Похожие товары" - на основе категории и бренда.
    """
    # Получаем исходный товар
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    source_product = result.scalar_one_or_none()
    
    if not source_product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    # Ищем похожие в той же категории
    result = await db.execute(
        select(Product)
        .where(
            and_(
                Product.id != product_id,
                Product.category_id == source_product.category_id,
                Product.is_active == True,
            )
        )
        .options(selectinload(Product.prices))
        .order_by(
            # Приоритет тем же брендом
            (Product.brand == source_product.brand).desc(),
            desc(Product.rating),
            desc(Product.views_count),
        )
        .limit(limit)
    )
    products = result.scalars().all()
    
    return [product_to_list_item(p) for p in products]


@router.get("/trending", response_model=List[ProductListItem])
async def get_trending_products(
    limit: int = Query(10, ge=1, le=20),
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Трендовые товары (на основе просмотров).
    """
    query = (
        select(Product)
        .where(Product.is_active == True)
        .options(selectinload(Product.prices))
    )
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    query = (
        query
        .order_by(desc(Product.views_count), desc(Product.rating))
        .limit(limit)
    )
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return [product_to_list_item(p) for p in products]


@router.get("/bestsellers", response_model=List[ProductListItem])
async def get_bestsellers(
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    Бестселлеры (на основе рейтинга и количества отзывов).
    """
    result = await db.execute(
        select(Product)
        .where(
            and_(
                Product.is_active == True,
                Product.review_count > 0,
            )
        )
        .options(selectinload(Product.prices))
        .order_by(desc(Product.rating), desc(Product.review_count))
        .limit(limit)
    )
    products = result.scalars().all()
    
    return [product_to_list_item(p) for p in products]


@router.get("/recently-viewed", response_model=List[ProductListItem])
async def get_recently_viewed(
    limit: int = Query(10, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Недавно просмотренные товары пользователя.
    """
    result = await db.execute(
        select(ViewHistory)
        .where(ViewHistory.user_id == current_user.id)
        .order_by(desc(ViewHistory.viewed_at))
        .limit(limit)
        .options(selectinload(ViewHistory.product).selectinload(Product.prices))
    )
    view_history = result.scalars().all()
    
    products = [vh.product for vh in view_history if vh.product and vh.product.is_active]
    
    return [product_to_list_item(p) for p in products]


@router.get("/category/{category_id}")
async def get_category_recommendations(
    category_id: int,
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    Рекомендации по категории (лучшие в категории).
    """
    result = await db.execute(
        select(Product)
        .where(
            and_(
                Product.category_id == category_id,
                Product.is_active == True,
            )
        )
        .options(selectinload(Product.prices))
        .order_by(desc(Product.rating), desc(Product.views_count))
        .limit(limit)
    )
    products = result.scalars().all()
    
    return [product_to_list_item(p) for p in products]


@router.post("/feedback")
async def submit_recommendation_feedback(
    product_id: int,
    feedback_type: str,  # "like", "dislike", "click", "purchase"
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Обратная связь по рекомендации (для обучения модели).
    
    В реальном приложении здесь бы записывались данные для ML-модели.
    """
    # Заглушка - в будущем можно сохранять в отдельную таблицу
    # для обучения рекомендательной системы
    return {
        "message": "Feedback received",
        "product_id": product_id,
        "feedback_type": feedback_type,
    }
