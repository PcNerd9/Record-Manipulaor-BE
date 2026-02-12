from sqlalchemy import Column, String, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as UUID_PKG
from typing import Any

from app.model.basemodel import BaseModel

class Task(BaseModel):
    __tablename__ = "tasks"
    
    job_id: Mapped[UUID_PKG] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    result: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)