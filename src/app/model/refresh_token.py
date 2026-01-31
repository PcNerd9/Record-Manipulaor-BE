from __future__ import annotations

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import UUID as UUID_PKG
from typing import TYPE_CHECKING

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
    
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False, init=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_used: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    user: Mapped["User"] = relationship(
        back_populates="refresh_tokens", uselist=False
    )
    
    