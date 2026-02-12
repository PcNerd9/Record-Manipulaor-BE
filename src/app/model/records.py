from __future__ import annotations
from sqlalchemy import String, ForeignKey, insert, Index, select, and_, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import uuid4, UUID as UUID_PKG
from typing import Any, TYPE_CHECKING, Self, Sequence
import math

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
        db: AsyncSession,
        dataset_id: str,
        key: str | None = None,
        value: str | None = None,
        page: int = 1,
        page_size: int = 100,
        sort_by: str | None = None,
        sort_order: str = "asc"
    ) -> dict[str, Any]:
        
        query = select(cls)
        count_qeuery = select(func.count()).select_from(cls)
        
        page = max(1, page)
        page_size = max(1, page_size)
        
        offset = ( page - 1) * page_size
        
        if key and value:
            and_condition = and_(
                        cls.dataset_id == dataset_id,
                        cls.data[key].astext.ilike(f"%{value}%")
                    )
            query = (
                query
                .where(
                    and_condition
                )     
            )
            
            count_qeuery = count_qeuery.where(and_condition)
        
        if sort_by:
            sort_column = cls.data[sort_by].astext
            print(sort_by)
            print(sort_column)
            if sort_order.lower() == "desc":
                query = query.order_by(sort_column.desc(), cls.id.desc())
            else:
                query = query.order_by(sort_column.asc(), cls.id.asc())

        else:
            query = query.order_by(cls.created_at.desc(), cls.id.desc())
            
        
        query = query.limit(page_size).offset(offset)
                
        
        
        count_result = await db.execute(count_qeuery)
        count = count_result.scalar() or 0
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        total_page = math.ceil(count / page_size)
        
        return {
            "records": records,
            "meta": {
                "page": page,
                "page_size": page_size,
                "total": count,
                "total_page": total_page,
                "has_next_page": total_page > page,
                "has_prev_page": page < 1
            }
        }