from sqlalchemy import String, DateTime, Boolean, func, select, and_, or_
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Any, Self, Sequence
import math

from uuid import uuid4, UUID as UUID_pkg
from datetime import datetime

from app.core.db.database import Base


class BaseModel(Base):
    __abstract__ = True
    
    id: Mapped[UUID_pkg] = mapped_column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4, init=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False, init=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, init=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, init=False)
    
    
    @classmethod
    async def create(cls, data: dict[str, Any], db: AsyncSession) -> Self:
        new_cls = cls(**data)
        db.add(new_cls)
        
        await db.flush()
        await db.refresh(new_cls)
        
        return new_cls
    
    async def save(self, db: AsyncSession) -> Self:
        
        self.updated_at = datetime.now(timezone.utc)
        db.add(self)
        
        await db.flush()
        await db.refresh(self)
        return self
    
    @classmethod
    async def bulk_save(cls, models: list | Sequence, db: AsyncSession):
        try:
            db.add_all(models);
        except Exception:
            await db.rollback()
            raise e
    
    def to_dict(self) -> dict[str, Any]:
        
        obj_dict = self.__dict__.copy()
        
        del obj_dict["_sa_instance_state"]
        
        for key, value in obj_dict.items():
            if isinstance(value, UUID_pkg):
                obj_dict[key] = str(value)
                
            elif isinstance(value, datetime):
                obj_dict[key] = value.isoformat()

        return obj_dict
    
    async def update(self, data: dict[str, Any], db: AsyncSession) -> Self:
        
        excluded_value = ["id", "created_at", "updated_at", "status"]
        
        for key, value in data.items():
            if key not in excluded_value:
                if hasattr(self, key) and value is not None:
                    setattr(self, key, value)
        
        await self.save(db)
        return self
    
    async def delete(self, db: AsyncSession): 
        await db.delete(self)
        await db.flush()
    
    @classmethod
    async def get_by_id(cls, id: str, db: AsyncSession) -> Self | None:
        stmt = select(cls).where(cls.id == id)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_unique(
        cls,
        key: str,
        value: Any,
        db: AsyncSession
    ) -> Self | None:
        
        
        if hasattr(cls, key):
            column = getattr(cls, key)
            result = await db.execute(select(cls).where(column == value))
            return result.scalar_one_or_none()
        
        return None
    
    
    @classmethod
    async def get_by(
        cls,
        db: AsyncSession,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 10,
        fetch_all: bool = False,
        is_active: bool = True,
        orderby: str | list[str] | None = None
    ) -> dict[str, Any]:

        base_query = select(cls)
        conditions = []

        if filters:
            for key, value in filters.items():
                if not hasattr(cls, key):
                    continue

                column = getattr(cls, key)

                if isinstance(value, str) and "%" in value:
                    conditions.append(column.ilike(value))
                elif value is None:
                    conditions.append(column.is_(None))
                else:
                    conditions.append(column == value)


        if is_active and hasattr(cls, "is_active"):
            conditions.append(cls.is_active.is_(True))

        if conditions:
            base_query = base_query.where(and_(*conditions))


        if orderby:
            if isinstance(orderby, str):
                orderby = [orderby]
            
            for field_expr in orderby:
                desc = field_expr.startswith("-")
                field = field_expr[1:] if desc else field_expr

                if hasattr(cls, field):
                    column = getattr(cls, field)
                    base_query = base_query.order_by(column.desc() if desc else column.asc())

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

    
        if page < 1:
            page = 1

        if page_size < 1:
            page_size = 10

        if page_size > 100:
            page_size = 100   # hard cap

        if not fetch_all:
            offset = (page - 1) * page_size
            base_query = base_query.offset(offset).limit(page_size)


        result = await db.execute(base_query)
        result_data = result.scalars().all()

        total_page = math.ceil(total_count / page_size)
        has_next_page = page < total_page
        has_prev_page = page > 1

        response: dict[str, Any] = {
            "data": result_data
        }
        response["meta"] = {
            "total": total_count
        }

        if not fetch_all:
            response["meta"]["page"] = page
            response["meta"]["page_size"] = page_size
            response["meta"]["total_page"] = total_page
            response["meta"]["has_next_page"] = has_next_page
            response["meta"]["has_prev_page"] = has_prev_page
            

        return response
    
    
    @classmethod
    async def bulk_get_by_ids(cls, ids: list[str], db: AsyncSession) -> Sequence[Self]:
        stmt = select(cls).where(cls.id.in_(ids))
        
        result = await db.execute(stmt)
        return result.scalars().all()
