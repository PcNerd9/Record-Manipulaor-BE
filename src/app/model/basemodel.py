from sqlalchemy import String, DateTime, func, select, and_, or_
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Any, Self

from uuid import uuid4, UUID as UUID_pkg
from datetime import datetime

from app.core.db.database import Base


class BaseModel(Base):
    __abstract__ = True
    
    id: Mapped[UUID_pkg] = mapped_column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4, init=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False, init=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False, init=False)
    
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
            result = await db.execute(select(column == value))
            return result.scalar_one_or_none()
        
        return None
        
        
        result = await db.execute(stmt)
        
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by(
        cls,
        db: AsyncSession,
        filter: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 10,
        all: bool = False,
        is_active: bool = True
    ) -> dict[str, Any]:
        
        query = select(cls)
        or_condition = []
        
        if filter:
            for key, value in filter.items():
                if hasattr(cls, key):
                    column = getattr(cls, key)
                    if isinstance(value, str) and "%" in value:
                        or_condition.append(column.ilike(value))
                    elif value is None:
                        or_condition.append(column.is_(None))
                    else:
                        or_condition.append(column == value)
        
        if or_condition:               
            if is_active and hasattr(cls, "is_active"):
                query = query.filter(
                    and_(
                        cls.is_active.is_(True), 
                        or_(*or_condition)
                    )
                )
            else:
                query = query.where(or_(*or_condition))
        
        # Set page and page size if invalid input
        if page < 0:
            page = 1
        
        if page_size <= 0:
            page_size = 10
            
        offset = (page - 1) * page_size
        
        if not all:
            query = query.offset(offset).limit(page_size)
        
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        
        result = await db.execute(query)
        result_data = result.scalars().all()
        count = count_result.scalar() or 0
        
        return_data = {
            "data": result_data,
            "count": count
        }
        
        if not all:
            return_data["page"] = page
            return_data["page_size"] = page_size
        
        return return_data