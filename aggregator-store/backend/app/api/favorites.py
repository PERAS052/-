"""
API роуты для избранного (favorites).
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.favorite import Favorite
from app.models.product import Product
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


@router.get("/", response_model=List[ProductListItem])
async def list_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Список избранных товаров пользователя.
    """
    result = await db.execute(
        select(Favorite)
        .where(Favorite.user_id == current_user.id)
        .options(
            selectinload(Favorite.product).selectinload(Product.prices)
        )
        .order_by(Favorite.created_at.desc())
    )
    favorites = result.scalars().all()
    
    return [product_to_list_item(f.product) for f in favorites]


@router.post("/{product_id}", status_code=status.HTTP_201_CREATED)
async def add_to_favorites(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Добавление товара в избранное.
    """
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
    
    # Проверяем, нет ли уже в избранном
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.product_id == product_id,
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Товар уже в избранном"
        )
    
    # Добавляем
    favorite = Favorite(
        user_id=current_user.id,
        product_id=product_id,
        created_at=datetime.utcnow(),
    )
    db.add(favorite)
    await db.commit()
    
    return {"message": "Товар добавлен в избранное"}


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_favorites(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Удаление товара из избранного.
    """
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.product_id == product_id,
            )
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден в избранном"
        )
    
    await db.delete(favorite)
    await db.commit()
    
    return None


@router.get("/{product_id}/check")
async def check_favorite(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Проверка, находится ли товар в избранном.
    """
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.product_id == product_id,
            )
        )
    )
    is_favorite = result.scalar_one_or_none() is not None
    
    return {"is_favorite": is_favorite}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Очистка всего избранного.
    """
    await db.execute(
        delete(Favorite).where(Favorite.user_id == current_user.id)
    )
    await db.commit()
    
    return None
