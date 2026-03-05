from typing import Any, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.core import exceptions
from app.models.user import User
from app.schemas.category import CategoryRead, CategoryCreate
from app.services import category_service

router = APIRouter()

@router.get("/", response_model=List[CategoryRead])
async def read_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve all valid task categories. Requires authentication.
    """
    categories = await category_service.get_categories(db, skip=skip, limit=limit)
    return categories

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new category. Requires authentication.
    """
    category = await category_service.get_category_by_name(db, name=category_in.name)
    if category:
        raise exceptions.get_already_exists_exception(detail="Category already exists.")
    
    category = await category_service.create_category(db, category_in=category_in)
    return category
