from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from uuid import uuid4, UUID as UUID_pkg
from datetime import datetime

from app.core.db.database import Base


class BaseModel(Base):
    __abstract__ = True
    
    id: Mapped[UUID_pkg] = mapped_column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4, init=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False, init=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, init=False)