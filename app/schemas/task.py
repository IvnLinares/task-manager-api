from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional
from datetime import datetime, timezone
from app.models.task import TaskStatus, TaskPriority
from app.schemas.category import CategoryRead
from app.schemas.attachment import AttachmentRead

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    category_ids: Optional[List[int]] = []
    
    @field_validator('due_date')
    def validate_due_date(cls, v):
        if v is not None:
            # Ensure the date is in the future
            if v < datetime.now(timezone.utc):
                raise ValueError("due_date must be in the future")
        return v

class TaskUpdate(TaskBase):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    category_ids: Optional[List[int]] = None
    
    @field_validator('due_date')
    def validate_due_date(cls, v):
        # We can allow past dates for updates if needed, but keeping strict for now
        if v is not None and v < datetime.now(timezone.utc):
            raise ValueError("due_date must be in the future")
        return v

class TaskRead(TaskBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    categories: List[CategoryRead] = []
    attachments: List[AttachmentRead] = []

    model_config = ConfigDict(from_attributes=True)
