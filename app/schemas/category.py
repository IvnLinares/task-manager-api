from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
