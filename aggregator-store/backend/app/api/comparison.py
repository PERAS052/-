"""
API роуты для сравнения товаров.
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.comparison_list import ComparisonList, comparison_items
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductResponse

router = APIRouter()


@router.get("/lists")
async def get_comparison_lists(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение всех списков сравнения пользователя.
    """
    result = await db.execute(
        select(ComparisonList)
        .where(ComparisonList.user_id == current_user.id)
        .order_by(ComparisonList.created_at.desc())
    )
    lists = result.scalars().all()
    
    return [
        {
            "id": cl.id,
            "name": cl.name,
            "description": cl.description,
            "products_count": len(cl.products),
            "max_items": cl.max_items,
            "is_active": cl.is_active,
            "created_at": cl.created_at,
            "last_viewed_at": cl.last_viewed_at,
        }
        for cl in lists
    ]


@router.get("/lists/{list_id}")
async def get_comparison_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение списка сравнения с товарами.
    """
    result = await db.execute(
        select(ComparisonList)
        .where(
            and_(
                ComparisonList.id == list_id,
                ComparisonList.user_id == current_user.id,
            )
        )
        .options(
            selectinload(ComparisonList.products)
            .selectinload(Product.prices)
            .selectinload(ProductPrice.marketplace)
        )
    )
    comp_list = result.scalar_one_or_none()
    
    if not comp_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Список сравнения не найден"
        )
    
    # Обновляем last_viewed_at
    comp_list.last_viewed_at = datetime.utcnow()
    await db.commit()
    
    # Формируем ответ с товарами
    products_data = []
    for product in comp_list.products:
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
                    "currency": price.currency,
                    "is_available": price.is_available,
                })
        
        products_data.append({
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "brand": product.brand,
            "images": product.images or [],
            "specifications": product.specifications or {},
            "rating": product.rating,
            "review_count": product.review_count,
            "prices": prices_info,
            "min_price": product.min_price,
        })
    
    return {
        "id": comp_list.id,
        "name": comp_list.name,
        "description": comp_list.description,
        "products": products_data,
        "max_items": comp_list.max_items,
    }


@router.post("/lists", status_code=status.HTTP_201_CREATED)
async def create_comparison_list(
    name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание нового списка сравнения.
    """
    comp_list = ComparisonList(
        user_id=current_user.id,
        name=name,
        max_items=4,  # По умолчанию максимум 4 товара для сравнения
        is_active=True,
    )
    db.add(comp_list)
    await db.commit()
    await db.refresh(comp_list)
    
    return {
        "id": comp_list.id,
        "name": comp_list.name,
        "message": "Список сравнения создан"
    }


@router.post("/lists/{list_id}/add/{product_id}")
async def add_to_comparison(
    list_id: int,
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Добавление товара в список сравнения.
    """
    # Получаем список
    result = await db.execute(
        select(ComparisonList)
        .where(
            and_(
                ComparisonList.id == list_id,
                ComparisonList.user_id == current_user.id,
            )
        )
        .options(selectinload(ComparisonList.products))
    )
    comp_list = result.scalar_one_or_none()
    
    if not comp_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Список сравнения не найден"
        )
    
    # Проверяем лимит
    if not comp_list.can_add_product():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Максимум {comp_list.max_items} товаров для сравнения"
        )
    
    # Проверяем существование товара
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    # Проверяем, не добавлен ли уже
    if comp_list.has_product(product_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Товар уже в списке сравнения"
        )
    
    # Добавляем
    comp_list.products.append(product)
    await db.commit()
    
    return {"message": "Товар добавлен к сравнению"}


@router.delete("/lists/{list_id}/remove/{product_id}")
async def remove_from_comparison(
    list_id: int,
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Удаление товара из списка сравнения.
    """
    result = await db.execute(
        select(ComparisonList)
        .where(
            and_(
                ComparisonList.id == list_id,
                ComparisonList.user_id == current_user.id,
            )
        )
        .options(selectinload(ComparisonList.products))
    )
    comp_list = result.scalar_one_or_none()
    
    if not comp_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Список сравнения не найден"
        )
    
    # Находим и удаляем товар из списка
    product_to_remove = next(
        (p for p in comp_list.products if p.id == product_id),
        None
    )
    
    if not product_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден в списке сравнения"
        )
    
    comp_list.products.remove(product_to_remove)
    await db.commit()
    
    return {"message": "Товар удалён из сравнения"}


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comparison_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Удаление списка сравнения.
    """
    result = await db.execute(
        select(ComparisonList).where(
            and_(
                ComparisonList.id == list_id,
                ComparisonList.user_id == current_user.id,
            )
        )
    )
    comp_list = result.scalar_one_or_none()
    
    if not comp_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Список сравнения не найден"
        )
    
    await db.delete(comp_list)
    await db.commit()
    
    return None
