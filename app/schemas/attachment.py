from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class AttachmentRead(BaseModel):
    id: int
    filename: str
    content_type: str
    size: int
    task_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
