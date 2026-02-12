from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Literal
from uuid import UUID
from datetime import datetime, timezone


from app.model.records import Record
from app.model.user import User
from app.model.dataset import Dataset
from app.core.exceptions.http_exceptions import ForbiddenException, NotFoundException, BadRequestException, ConflictException
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
        
        return dataset
        
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
        
        is_valid_column, reason = record_repository.validate_record_payload(record_data["data"], dataset.data_schema)
        if not is_valid_column:
            raise BadRequestException(reason)
            
        record = await Record.create({"dataset_id": dataset_id, "data": record_data}, db)
        dataset.row_count += 1
        await dataset.save(db);
        
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
            orderby=["-created_at", "-id"]
        )
        
        record_dicts = [record.to_dict() for record in records["data"]]
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="successfully fetched paginated records",
            data={
                "records": record_dicts,
                "meta": records["meta"]
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
        
        is_valid_column, reason =  record_repository.validate_record_payload(record_data["data"], dataset.data_schema, allow_partial=True)
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
        
    async def batch_update(
        self,
        update_data: list[dict[str, Any]],
        dataset_id: str,
        db: AsyncSession,
        user: User
    ):

        if not update_data:
            raise BadRequestException("No updates provided")
        
        # Validate input structure
        record_ids = []
        payload_map: dict[str, Any] = {}
        
        for item in update_data:
            record_id = item.get("id")
            data = item.get("data")
            
            if not record_id or not is_valid_uuid(record_id):
                raise BadRequestException(f"Invalid  record id: {record_id}")
            
            if not isinstance(data, dict):
                raise BadRequestException(f"Invalid data payload for  record: {record_id}")
            
            record_ids.append(record_id)
            payload_map[record_id] = data
            
        # Bulk fetch records
        records = await Record.bulk_get_by_ids(record_ids, db)
        
        if len(records) != len(record_ids):
            found_ids = {str(r.id) for r in records}
            missing = set(record_ids) - found_ids
            raise NotFoundException(f"Records not found: {list(missing)}")
        
        dataset_ids = {str(r.dataset_id) for r in records}
        
        datasets = await Dataset.bulk_get_by_ids(list(dataset_ids), db)
        
        dataset_map = {str(d.id): d for d in datasets}
        
        # Validate Dataset Ownership
        for dataset_id, dataset in dataset_map.items():
            if dataset.user_id != user.id:
                raise ForbiddenException("Dataset Not yours")
            
        # Validate Schema And merge updates (in-memory)
        for record in records:
            dataset = dataset_map[str(record.dataset_id)]
            payload = payload_map[str(record.id)]
            
            is_valid, reason = record_repository.validate_record_payload(
                payload=payload,
                dataset_schema=dataset.data_schema,
                allow_partial=True
            )
            
            if not is_valid:
                raise BadRequestException(
                    f"Schema validation failed for record {record.id}: {reason}"
                )
                
            record.data = {**record.data, **payload}
            record.updated_at = datetime.now(timezone.utc)
        
        await Record.bulk_save(records, db)
        
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message=f"{len(records)} records updated successfully",
            data=[r.to_dict() for r in records]
        )
        
        
    # Delete record
    async def delete_record(
        self,
        dataset_id: str,
        record_id: str,
        user: User,
        db: AsyncSession
    ):
        if not is_valid_uuid(record_id):
            raise BadRequestException("Invalid record Id")
        
        if not is_valid_uuid(dataset_id):
            raise BadRequestException("Invalid dataset Id")
        
        record = await Record.get_by_id(id=record_id, db=db)
        if not record:
            raise NotFoundException("Record not found")
        
        if str(record.dataset_id) != dataset_id:
            raise ConflictException("Record doesn't belong to dataset")
        
        dataset = await self._validate_ownership(str(record.dataset_id), user.id, db=db)
        
        # Decrease dataset row count
        await dataset.update({"row_count": dataset.row_count - 1}, db)
        
        await record.delete(db)
        
        
        
        
        
    
    async def filter_record_by_column(
        self,
        dataset_id: str,
        db: AsyncSession,
        user: User,
        key: str | None = None,
        value: str | None = None,
        page_size: int = 100,
        page: int = 1,
        sort_by: str | None = None,
        sort_order: Literal["asc", "desc"] = "asc"
    ) -> dict[str, Any]: 
        
        await self._validate_ownership(dataset_id, user.id, db)
        
        records = await Record.filter_records(
            key=key, 
            value=value, 
            db=db, 
            dataset_id=dataset_id, 
            page_size=page_size, 
            page=page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        record_dicts = [record.to_dict() for record in records["records"]]
        
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="successfully filter records by column",
            data={
                "records": record_dicts,
                "meta": records["meta"]
            }
        )


record_service = RecordService()