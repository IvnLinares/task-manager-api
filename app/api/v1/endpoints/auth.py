from typing import Annotated, Any
from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rate_limit import limiter

from app.db.session import get_db
from app.schemas.user import UserRead, UserCreate
from app.services import auth_service
from app.core import security, exceptions
from app.models.user import User

router = APIRouter()

# Schema for token responses (We could extract this to a token schema file later)
from pydantic import BaseModel
class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Registers a new user.
    """
    # Check if user exists
    user = await auth_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise exceptions.get_already_exists_exception(detail="A user with this email already exists.")
    
    # Create new user
    new_user = await auth_service.create_user(db, user_in)
    return new_user

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Authenticate user using the credentials from the form
    user = await auth_service.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise exceptions.get_incorrect_login_exception()
    elif not user.is_active:
        raise exceptions.get_inactive_user_exception()
    
    # Generate token
    access_token = security.create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}
