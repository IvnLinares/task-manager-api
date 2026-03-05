from typing import Any, List, Optional
from fastapi import APIRouter, Depends, status, Query, UploadFile, File
import os
import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.core import exceptions
from app.models.user import User
from app.models.task import TaskStatus, TaskPriority
from app.schemas.task import TaskRead, TaskCreate, TaskUpdate
from app.schemas.attachment import AttachmentRead
from app.services import task_service

router = APIRouter()

@router.get("/", response_model=List[TaskRead])
async def read_tasks(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Skip a number of results for pagination"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of results to return"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search term for task title and description"),
    sort_by: str = Query("created_at", description="Field to sort by (e.g. created_at, due_date)"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order (asc or desc)"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve tasks for the logged-in user with support for query parameters 
    such as filtering, sorting, and pagination.
    """
    tasks = await task_service.get_tasks(
        db=db, user_id=current_user.id, skip=skip, limit=limit,
        status=status,
        priority=priority,
        category_id=category_id,
        search=search,
        sort_by=sort_by, sort_order=sort_order
    )
    return tasks

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new task.
    """
    task = await task_service.create_task(db=db, task_in=task_in, user_id=current_user.id)
    return task

@router.get("/{task_id}", response_model=TaskRead)
async def read_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a single task by ID.
    """
    task = await task_service.get_task_by_id(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise exceptions.get_not_found_exception(detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a task.
    """
    task = await task_service.get_task_by_id(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise exceptions.get_not_found_exception(detail="Task not found")
    
    task = await task_service.update_task(db=db, db_task=task, task_in=task_in)
    return task

@router.delete("/{task_id}", response_model=TaskRead)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a task.
    """
    task = await task_service.get_task_by_id(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise exceptions.get_not_found_exception(detail="Task not found")
        
    task = await task_service.delete_task(db=db, db_task=task)
    return task

@router.post("/{task_id}/upload", response_model=AttachmentRead, status_code=status.HTTP_201_CREATED)
async def upload_task_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Upload a file attachment for a task.
    """
    task = await task_service.get_task_by_id(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise exceptions.get_not_found_exception(detail="Task not found")
        
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{task_id}_{file.filename}"
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        while content := await file.read(1024 * 1024):
            await out_file.write(content)
            
    from app.models.attachment import Attachment
    attachment = Attachment(
        filename=file.filename,
        file_path=file_path,
        content_type=file.content_type,
        size=file_size,
        task_id=task_id
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    return attachment

