from __future__ import annotations
from sqlalchemy import String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from uuid import uuid4, UUID as UUID_PKG
from typing import Any, TYPE_CHECKING

from app.model.basemodel import BaseModel

if TYPE_CHECKING:
    from app.model.records import Record
    from app.model.user import User


class Dataset(BaseModel):
    __tablename__ = "datasets"
    
    user_id: Mapped[UUID_PKG] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    data_schema: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    column_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    
    records: Mapped[list["Record"]] = relationship(
        "Record", back_populates="dataset", lazy="selectin", init=False, cascade="all, delete-orphan"
    )
    
    user: Mapped["User"] = relationship(
        "User", back_populates="datasets", uselist=False, init=False
    )