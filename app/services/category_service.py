from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.category import Category
from app.schemas.category import CategoryCreate

async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Category]:
    """Retrieve all categories with pagination."""
    result = await db.execute(select(Category).offset(skip).limit(limit))
    return result.scalars().all()

async def get_category_by_name(db: AsyncSession, name: str) -> Optional[Category]:
    """Retrieve a category by exact name."""
    result = await db.execute(select(Category).filter(Category.name == name))
    return result.scalars().first()

async def create_category(db: AsyncSession, category_in: CategoryCreate) -> Category:
    """Create a new category."""
    db_category = Category(name=category_in.name)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category
