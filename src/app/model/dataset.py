from __future__ import annotations
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from uuid import uuid4, UUID as UUID_PKG
from typing import Any, TYPE_CHECKING

from app.model.basemodel import BaseModel

if TYPE_CHECKING:
    from app.model.records import Record


class Dataset(BaseModel):
    __tablename__ = "datasets"
    
    user_id: Mapped[UUID_PKG] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    data_schema: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    records: Mapped["Record"] = relationship(
        "Record", back_populates="dataset", lazy="selectin", init=False
    )