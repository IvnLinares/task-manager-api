from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, and_, asc, desc

from app.models.task import Task, TaskStatus, TaskPriority
from app.models.category import Category
from app.schemas.task import TaskCreate, TaskUpdate

async def get_task_by_id(db: AsyncSession, task_id: int, user_id: int) -> Optional[Task]:
    """Retrieve a single task belonging to a specific user by its ID."""
    query = select(Task).options(
        selectinload(Task.categories),
        selectinload(Task.attachments)
    ).filter(
        and_(Task.id == task_id, Task.owner_id == user_id)
    )
    result = await db.execute(query)
    return result.scalars().first()

async def get_tasks(
    db: AsyncSession, 
    user_id: int,
    skip: int = 0, 
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> List[Task]:
    """
    Retrieve all tasks for the current user with optional filtering, pagination, and sorting.
    """
    query = select(Task).options(
        selectinload(Task.categories),
        selectinload(Task.attachments)
    ).filter(Task.owner_id == user_id)
    
    # Filtering
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if category_id:
        query = query.filter(Task.categories.any(Category.id == category_id))
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term)
            )
        )
        
    # Sorting
    sort_column = getattr(Task, sort_by, Task.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
        
    # Pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())

async def create_task(db: AsyncSession, task_in: TaskCreate, user_id: int) -> Task:
    """Create a new task, associating it with the requested categories and the user."""
    # Build core task object
    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        owner_id=user_id
    )
    
    # Handle many-to-many relationship with categories
    if task_in.category_ids:
        cat_query = select(Category).filter(Category.id.in_(task_in.category_ids))
        cat_result = await db.execute(cat_query)
        categories = list(cat_result.scalars().all())
        db_task.categories = categories

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    
    # We load relations to return a complete Pydantic matching model
    return await get_task_by_id(db, task_id=db_task.id, user_id=user_id)

async def update_task(db: AsyncSession, db_task: Task, task_in: TaskUpdate) -> Task:
    """Update an existing task in the database."""
    update_data = task_in.model_dump(exclude_unset=True)
    
    # Handle standard fields
    for field, value in update_data.items():
        if field != "category_ids" and hasattr(db_task, field):
            setattr(db_task, field, value)
            
    # Handle category relationship modifications if provided
    if "category_ids" in update_data and update_data["category_ids"] is not None:
        cat_query = select(Category).filter(Category.id.in_(update_data["category_ids"]))
        cat_result = await db.execute(cat_query)
        db_task.categories = list(cat_result.scalars().all())
        
    await db.commit()
    await db.refresh(db_task)
    
    return db_task

async def delete_task(db: AsyncSession, db_task: Task) -> Task:
    """Deletes a task from the database."""
    await db.delete(db_task)
    await db.commit()
    return db_task
