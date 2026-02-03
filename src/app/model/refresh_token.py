from __future__ import annotations

from sqlalchemy import String, DateTime, ForeignKey, func, select
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from uuid import UUID as UUID_PKG
from typing import TYPE_CHECKING, Self

from app.model.basemodel import BaseModel

if TYPE_CHECKING:
    from app.model.user import User


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"
    
    user_id: Mapped[UUID_PKG] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    token: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    session_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    device_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    ip_address: Mapped[str] = mapped_column(String, nullable=False)
    user_agent: Mapped[str] = mapped_column(String, nullable=False)
    jti: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False, init=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_used: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    user: Mapped["User"] = relationship(
        back_populates="refresh_tokens", uselist=False
    )
    
    @classmethod
    async def get_token_by_user_and_device_id(
        cls, user_id: str, device_id: str, db: AsyncSession
    ) -> Self | None:
        
        stmt = select(cls).where(cls.user_id == user_id, cls.device_id == device_id)
        result = await db.execute(stmt)
        
        return result.scalar_one_or_none()
    
    async def revoke(self, db: AsyncSession) -> None:
        await self.delete(db)
        
    @classmethod
    async def create_refresh_token(
        cls,
        user_id: str,
        token: str,
        device_id: str,
        jti: str,
        user_agent: str,
        ip_address: str,
        expires_at: datetime,
        db: AsyncSession
    ) -> Self:
        
        existing_token = await cls.get_token_by_user_and_device_id(user_id, device_id, db)
        if existing_token:
            await existing_token.revoke(db)
            
        refresh_token = await cls.create(
            {
                "user_id": user_id,
                "token": token,
                "device_id": device_id,
                "user_agent": user_agent,
                "jti": jti,
                "ip_address": ip_address,
                "expires_at": expires_at,
                "issued_at": datetime.now(timezone.utc),
                "last_used": datetime.now(timezone.utc)
            }, 
            db
        )
        return refresh_token