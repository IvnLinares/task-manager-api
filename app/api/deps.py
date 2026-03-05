from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.core import exceptions
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.services import auth_service

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise exceptions.get_credentials_exception()
        # we parse the string ID to int
        parsed_user_id = int(user_id)
    except (JWTError, ValueError):
        raise exceptions.get_credentials_exception()
    
    # We don't have a get_user_by_id in auth_service, we'd need to fetch by id
    # Since we don't, I'll fetch directly here or we should add get_user to auth_service
    from sqlalchemy.future import select
    result = await db.execute(select(User).filter(User.id == parsed_user_id))
    user = result.scalars().first()
    
    if not user:
        raise exceptions.get_not_found_exception(detail="User not found")
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise exceptions.get_inactive_user_exception()
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_superuser:
        raise exceptions.get_forbidden_exception()
    return current_user
