from pydantic import BaseModel
from typing import Optional

# Shared properties
class UserBase(BaseModel):
    email: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

# Properties to return via API
class UserRead(UserBase):
    id: int

    # Enables reading from SQLAlchemy models
    model_config = {"from_attributes": True}
