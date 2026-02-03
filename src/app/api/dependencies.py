from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.db.database import async_get_db
from app.core.security import verify_token, TokenType
from app.core.exceptions.http_exceptions import UnauthorizedException, ForbiddenException
from app.model.user import User

http_bearer = HTTPBearer()


tokenDep = Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]
dbDepSession = Annotated[AsyncSession, Depends(async_get_db)]


async def get_current_user(
    auth: tokenDep,
    db: dbDepSession
):
    payload = await verify_token(auth.credentials, TokenType.ACCESS)
    if not payload:
        raise UnauthorizedException("Invalid Token")

    user_id = payload.get("sub", None)
    if not user_id:
        raise UnauthorizedException("Invalid Token")
    
    user = await User.get_by_id(user_id, db)
    if not user:
        raise UnauthorizedException("Invalid Token")
    
    return user

currentUser = Annotated[User, Depends(get_current_user)]

async def get_active_current_user(
    user: currentUser
):
    if not user.is_active or not user.is_deleted:
        raise ForbiddenException("Account has been suspended")
    
    return user

ActiveCurrentUser = Annotated[User, Depends(get_active_current_user)]