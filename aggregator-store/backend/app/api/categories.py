"""
API роуты для категорий товаров.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, require_manager, get_optional_user
from app.models.category import Category
from app.models.user import User
from app.schemas.category import (
    CategoryResponse,
    CategoryCreate,
    CategoryUpdate,
    CategoryTree,
)

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    parent_id: int = None,
    only_active: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """
    Список категорий.
    
    - **parent_id**: Фильтр по родительской категории
    - **only_active**: Только активные категории
    """
    query = select(Category)
    
    if parent_id is not None:
        query = query.where(Category.parent_id == parent_id)
    else:
        query = query.where(Category.parent_id.is_(None))
    
    if only_active:
        query = query.where(Category.is_active == True)
    
    query = query.order_by(Category.sort_order, Category.name)
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return categories


@router.get("/tree", response_model=List[CategoryTree])
async def get_category_tree(
    db: AsyncSession = Depends(get_db),
):
    """
    Получение дерева категорий с вложенными подкатегориями.
    """
    # Получаем все категории
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.level, Category.sort_order, Category.name)
    )
    categories = result.scalars().all()
    
    # Строим дерево
    category_map = {cat.id: cat for cat in categories}
    root_categories = []
    
    for cat in categories:
        cat.children = []  # Инициализируем список детей
        if cat.parent_id is None:
            root_categories.append(cat)
        else:
            parent = category_map.get(cat.parent_id)
            if parent:
                parent.children.append(cat)
    
    return root_categories


@router.get("/{slug}", response_model=CategoryResponse)
async def get_category(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Получение категории по slug.
    """
    result = await db.execute(
        select(Category).where(Category.slug == slug)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    
    return category


@router.get("/{slug}/breadcrumbs")
async def get_category_breadcrumbs(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Получение breadcrumb цепочки для категории.
    """
    result = await db.execute(
        select(Category).where(Category.slug == slug)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    
    # Строим цепочку
    breadcrumbs = []
    current = category
    
    while current:
        breadcrumbs.insert(0, {
            "id": current.id,
            "name": current.name,
            "slug": current.slug,
        })
        if current.parent_id:
            result = await db.execute(
                select(Category).where(Category.id == current.parent_id)
            )
            current = result.scalar_one_or_none()
        else:
            current = None
    
    return {"breadcrumbs": breadcrumbs}


# =============================================================================
# Admin endpoints
# =============================================================================

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание категории (только для менеджеров).
    """
    # Проверяем уникальность slug
    result = await db.execute(
        select(Category).where(Category.slug == category_data.slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория с таким slug уже существует"
        )
    
    # Определяем уровень
    level = 0
    if category_data.parent_id:
        result = await db.execute(
            select(Category).where(Category.id == category_data.parent_id)
        )
        parent = result.scalar_one_or_none()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Родительская категория не найдена"
            )
        level = parent.level + 1
    
    new_category = Category(
        name=category_data.name,
        slug=category_data.slug,
        description=category_data.description,
        image_url=category_data.image_url,
        parent_id=category_data.parent_id,
        level=level,
        sort_order=category_data.sort_order,
        is_active=category_data.is_active,
    )
    
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    
    return new_category


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновление категории.
    """
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    
    # Проверяем slug если меняется
    if category_update.slug and category_update.slug != category.slug:
        result = await db.execute(
            select(Category).where(Category.slug == category_update.slug)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Категория с таким slug уже существует"
            )
        category.slug = category_update.slug
    
    if category_update.name is not None:
        category.name = category_update.name
    if category_update.description is not None:
        category.description = category_update.description
    if category_update.image_url is not None:
        category.image_url = category_update.image_url
    if category_update.sort_order is not None:
        category.sort_order = category_update.sort_order
    if category_update.is_active is not None:
        category.is_active = category_update.is_active
    
    # Обновляем parent и level
    if category_update.parent_id is not None:
        if category_update.parent_id:
            result = await db.execute(
                select(Category).where(Category.id == category_update.parent_id)
            )
            parent = result.scalar_one_or_none()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Родительская категория не найдена"
                )
            category.level = parent.level + 1
        else:
            category.level = 0
        category.parent_id = category_update.parent_id
    
    await db.commit()
    await db.refresh(category)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db),
):
    """
    Удаление категории (soft delete).
    """
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    
    # Проверяем есть ли подкатегории
    result = await db.execute(
        select(Category).where(Category.parent_id == category_id)
    )
    children = result.scalars().all()
    
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить категорию с подкатегориями"
        )
    
    # Soft delete
    category.is_active = False
    await db.commit()
    
    return None
