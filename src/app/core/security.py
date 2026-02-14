from passlib.context import CryptContext
from jose import JWTError, jwt
from uuid import uuid4
from enum import Enum
from datetime import timedelta, datetime, timezone
from typing import Any
import secrets, string
from fastapi.responses import Response
import hmac, hashlib

from app.core.redis import get_redis
from app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)



class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_pasword(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
    sub: str,
    expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire_timestamp= int(expire.timestamp())
    to_encode = {
        "sub": sub, 
        "exp": expire_timestamp, 
        "type": TokenType.ACCESS, 
        "jti": str(uuid4())
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)

def create_refresh_token(
    sub: str,
    expires_delta: timedelta | None = None
) -> tuple[str, str]:    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    expire_timestamp = int(expire.timestamp())
    jti = str(uuid4())
    to_encode = {
        "sub": sub, 
        "exp": expire_timestamp, 
        "type": TokenType.REFRESH, 
        "jti": jti
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM), jti

def compute_blacklist_key(id: str) -> str:
    return f"blacklisted:{id}"


async def verify_token(token, expected_token_type: TokenType) -> dict[str, Any] | None:
    
    redis_client = await get_redis()
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY.get_secret_value(), 
            algorithms=[settings.ALGORITHM]
        )
        
        jti = payload.get("jti")
        token_type = payload.get("type")

        if token_type != expected_token_type or not jti:
            return None
        
        
        key = compute_blacklist_key(jti)
        
        blacklisted = await redis_client.get(key)
        
        if blacklisted:
            return None
                
        return payload
    
    except JWTError: 
        return None
    

def hash_token(token) -> str:
    return hmac.new(
        settings.SECRET_KEY.get_secret_value().encode(), token.encode(), hashlib.sha256
    ).hexdigest()
    
def verify_hash_token(token: str, hashed_token: str) -> bool:
    new_hash_token = hash_token(token)
    return new_hash_token == hashed_token

    
async def blacklist_token(token: str) -> bool:
    redis_client = await get_redis()
    
    try:
        paylaod = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM]
        )
        jti = paylaod.get("jti")
        
        if not jti:
            return False
        
        exp = paylaod.get("exp")
        if exp:
            remaining_time = datetime.fromtimestamp(exp, tz=timezone.utc)
            remaining_seconds = int((remaining_time - datetime.now(timezone.utc)).total_seconds())
        else:
            remaining_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        key = compute_blacklist_key(jti)
        
        await redis_client.setex(key, remaining_seconds, "1")
        
        return True
    except JWTError:
        return False
    
    
def generate_otp(length: int) -> str:
    digits = string.digits
    
    return "".join(secrets.choice(digits) for _ in range(length))

def set_cookeies(response: Response, key: str, value: str, max_age: int) -> None:
    if settings.ENVIRONMENT == "production":
        response.set_cookie(
            key=key,
            value=value,
            max_age=max_age,
            httponly=True,
            samesite="none",
            secure=True
        )
    else:
        response.set_cookie(
            key=key, value=value, max_age=max_age, path="/", httponly=True
        )

def delete_cookies(response: Response, key: str) -> None:
    if settings.ENVIRONMENT == "production":
        response.delete_cookie(
            key=key,
            httponly=True,
            samesite="none",
            secure=True
        )
    else:
        response.delete_cookie(
            key=key,
            path="/",
            httponly=True
        )

