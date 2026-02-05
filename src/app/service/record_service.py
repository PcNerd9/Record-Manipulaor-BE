from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from uuid import UUID


from app.model.records import Record
from app.model.user import User
from app.model.dataset import Dataset
from app.core.exceptions.http_exceptions import ForbiddenException, NotFoundException, BadRequestException
from app.repositories.record_repository import record_repository
from app.core.response import response_builder
from app.core.utils.helper import is_valid_uuid



class RecordService:
    async def _validate_ownership(
        self,
        dataset_id: str,
        user_id: UUID,
        db: AsyncSession
    ) -> Dataset:
        dataset = await Dataset.get_by_id(id=dataset_id, db=db)
        if not dataset:
            raise NotFoundException("Dataset not found")
        if dataset.user_id != user_id:
            raise ForbiddenException("Dataset not yours")
        
        return Dataset
        
    async def create_record(
        self,
        db: AsyncSession,
        dataset_id: str,
        user: User,
        record_data: dict[str, Any]
        
    ):
        if not is_valid_uuid(dataset_id):
            raise BadRequestException("Invalid dataset id")
        
        # Validate if dataset belongs to the user
        dataset = await self._validate_ownership(dataset_id, user.id, db)
        
        is_valid_column, reason = record_repository.validate_record_payload(record_data, dataset.data_schema)
        if not is_valid_column:
            raise BadRequestException(reason)
            
        record = await Record.create({"dataset_id": dataset_id, "data": record_data}, db)
        
        return response_builder(
            status_code=status.HTTP_201_CREATED,
            status="success",
            message="successfully created a new record",
            data=record.to_dict()
        )
        
    # Get all the records in a dataset, paginated
    async def get_records_for_dataset(
        self,
        dataset_id: str,
        user: User,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10
    ):
        if not is_valid_uuid(dataset_id):
            raise BadRequestException("Invalid dataset Id")

        # Validate if dataset belongs to the user
        await self._validate_ownership(dataset_id, user.id, db)
        
        records = await Record.get_by(
            db,
            {"dataset_id": dataset_id},
            page,
            page_size,
            orderby="-created_at"
        )
        
        record_dicts = [record.to_dict() for record in records["data"]]
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="successfully fetched paginated records",
            data={
                "records": record_dicts,
                "page": records["page"],
                "page_size": records["page_size"],
                "count": records["count"]
            }
        )
    
    
    # Get a record by id
        
    # update a record
    async def update_record(
        self,
        record_id: str,
        record_data: dict[str, Any],
        db: AsyncSession,
        user: User
    ):
        if not is_valid_uuid(record_id):
            raise BadRequestException("Invalid record id")
        
        record = await Record.get_by_id(id=record_id, db=db)
        if not record:
            raise NotFoundException("Record not found")
        
        dataset = await self._validate_ownership(str(record.dataset_id), user.id, db=db)
        
        is_valid_column, reason =  record_repository.validate_record_payload(record_data, dataset.data_schema, allow_partial=True)
        if not is_valid_column:
            raise BadRequestException(reason)
        
        updated_data = { **record.data, **record_data}
        
        record = await record.update(updated_data, db)
        
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="successfully update record",
            data=record.to_dict()
        )
        
        
    # Delete record
    async def delete_record(
        self,
        record_id: str,
        user: User,
        db: AsyncSession
    ):
        if not is_valid_uuid(record_id):
            raise BadRequestException("Invalid record Id")
        
        record = await Record.get_by_id(id=record_id, db=db)
        if not record:
            raise NotFoundException("Record not found")
        
        await self._validate_ownership(str(record.dataset_id), user.id, db=db)
        
        await record.delete(db)
        
    
    async def filter_record_by_column(
        self,
        dataset_id: str,
        key: str,
        value: str,
        db: AsyncSession,
        user: User,
        limit: int = 100
    ) -> dict[str, Any]: 
        
        await self._validate_ownership(dataset_id, user.id, db)
        
        records = await Record.filter_records(key, value, db, dataset_id, limit)
        
        record_dicts = [record.to_dict() for record in records]
        
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="successfully filter records by column",
            data={"records": record_dicts}
        )


record_service = RecordService()