from __future__ import annotations
from sqlalchemy import String, ForeignKey, insert, Index, select, and_
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import uuid4, UUID as UUID_PKG
from typing import Any, TYPE_CHECKING, Self, Sequence

from app.model.basemodel import BaseModel

if TYPE_CHECKING:
    from src.app.model.dataset import Dataset


class Record(BaseModel):
    __tablename__ = "records"
    
    dataset_id: Mapped[UUID_PKG] = mapped_column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="records", uselist=False, init=False
    )
    
    __table_args__ = (
        Index(
            "idx_records_data_gin",
            "data",
            postgresql_using="gin"
        ),
    )
    
    @classmethod
    async def bulk_insert_records(
        cls,
        dataset_id: str,
        records: list[dict[str, Any]],
        db: AsyncSession,
        batch_size: int = 100
    ):
        total = len(records)

        for i in range(0, total, batch_size):
            batch = records[i:i+batch_size]

            payload = [
                {
                    "dataset_id": dataset_id,
                    "data": row
                }
                for row in batch
            ]

            stmt = insert(Record).values(payload)
            await db.execute(stmt)
    
    
    @classmethod
    async def get_all_by_dataset(
        cls,
        dataset_id: str,
        db: AsyncSession
    ) -> Sequence[Self]:
        result = await db.execute(select(cls).where(cls.dataset_id == dataset_id))
        return result.scalars().all()
    
    
    @classmethod
    async def filter_records(
        cls,
        key: str,
        value: str,
        db: AsyncSession,
        dataset_id: str,
        limit: int = 100
    ) -> Sequence[Self]:
        
        smt = (
            select(cls)
            .where(
                and_(
                    Record.dataset_id == dataset_id,
                    Record.data[key].astext == value
                )
            ).limit(limit)
        )
        
        result = await db.execute(smt)
        return result.scalars().all()