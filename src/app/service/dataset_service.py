from fastapi import UploadFile, status, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
import structlog
from uuid import UUID
import pandas as pd
from io import BytesIO

from app.model.dataset import Dataset
from app.model.records import Record
from app.model.user import User
from app.repositories.dataset_repositories import dataset_repository, FileValidationError
from app.core.exceptions.http_exceptions import BadRequestException, NotFoundException, ForbiddenException
from app.core.response import response_builder
from app.core.utils.helper import is_valid_uuid

logger = structlog.get_logger(__name__)

class DatasetService():
    async def create_dataset(
        self,
        db: AsyncSession,
        file: UploadFile,
        user_id: UUID,

    ) -> dict[str, Any]:

        try:
            df = await dataset_repository.validate_and_parse_upload(file)
            
        except FileValidationError as e:
            raise BadRequestException(str(e))
        
        except Exception as e:
            
            logger.error("File Processing", filename=file.filename, reason=str(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File processing failed due to server error")
        
        schema = dataset_repository.infer_schema(df)

        data = {
            "user_id": user_id,
            "name": file.filename,
            "data_schema": schema
        }
        dataset = await Dataset.create(data, db)

        normalized_rows = dataset_repository.normalize_records(df)
        
        await Record.bulk_insert_records(db=db, dataset_id=str(dataset.id), records=normalized_rows)
        
        dataset_response = {
            "dataset_id": str(dataset.id),
            "rows": len(df),
            "columns": list(df.columns)
        }
        
        return response_builder(
            status_code=status.HTTP_201_CREATED,
            status="success",
            message="successfully upload",
            data=dataset_response
        )
    
    # Get all dateset  for user
    async def get_dataset_by_user(
        self,
        db: AsyncSession,
        user: User,
        name: str | None = None,
        page: int | None = 1,
        page_size: int | None = 10        
    ):
        filters: dict[str, Any] = {
            "user_id": user.id
        }  
        if name:
            filters["name"] = f"%{name}%"
            
        datasets = await Dataset.get_by(db=db, filters=filters, page=page, page_size=page_size)
        
        datasets_dict = [dataset.to_dict() for dataset in datasets["data"]]
        
        response_data = {
            "datasets": datasets_dict,
            "page": datasets["page"],
            "page_size": datasets["page_size"],
            "total": datasets["count"]
        }  
        
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="Successfully fetched user dataset",
            data=response_data
        )   
    
    # Get dataset by ID
    async def get_dataset(
        self,
        id: str, 
        user: User,
        db: AsyncSession
    ):
        if not is_valid_uuid(id):
            raise BadRequestException("Invalid Id")
        
        dataset = await Dataset.get_by_id(id=id, db=db)
        if not dataset:
            raise NotFoundException("Dataset not found")
        if dataset.user_id != user.id:
            raise ForbiddenException("Can only view your dataset")
        
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="successfully fetch dataset",
            data=dataset.to_dict()
        )
    
    # delete dataset
    async def delete_dataset(
        self,
        user: User,
        id: str,
        db: AsyncSession
    ):
        if not is_valid_uuid(id):
            raise BadRequestException("Invalid Id")
        
        dataset = await Dataset.get_by_id(id=id, db=db)
        if not dataset:
            raise NotFoundException("Dataset not found")
        
        if dataset.user_id != user.id:
            raise ForbiddenException("Can only delete your dataset")
        
        await dataset.delete(db)
        
    
    async def export_dataset(
        self,
        dataset_id: str,
        db: AsyncSession,
        user: User,
        format: str = "csv",
    ):
        if not is_valid_uuid(dataset_id):
            raise BadRequestException("Invalid Id")
            
        dataset = await Dataset.get_by_id(dataset_id, db)
        
        if not dataset:
            raise NotFoundException("Dataset not found")
        if dataset.user_id != user.id:
            raise ForbiddenException("File not yours")
        
        records = await Record.get_all_by_dataset(dataset_id, db)
        
        rows = [record.data for record in records]
        
        df = pd.DataFrame(rows)
        
        filename = dataset.name.split(".")[0]
        if format == "csv":
            file = df.to_csv(index=False)
            return Response(
                content=file,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}.csv"}               
            )
        elif format == "xlsx" or format == "xls":
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)
            
            return Response(
                content=buffer.read(),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"}
            )
        else:
            raise BadRequestException("Invalid export format")
    
    
    
dataset_service = DatasetService()