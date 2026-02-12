from pydantic import Field, BaseModel, field_serializer
from typing import Any, Annotated
from uuid import UUID
from datetime import datetime

from app.schemas.base_response import BaseResponse, BasePaginatedResponseSchema


class RecordBase(BaseModel):
    data: Annotated[dict[str, Any], Field(description="A Json of the column where key is the column name and value is the value for that column")]
    
class RecordCreate(RecordBase):
    ...

class RecordUpdate(RecordBase):
    ...

class RecordResponseSchema(RecordBase):
    id: Annotated[UUID, Field(description="Tue record Id")]
    dataset_id: Annotated[UUID, Field(description="Dataset id the record belong to")]
    created_at: Annotated[datetime, Field(description="Date record is created at")]
    updated_at: Annotated[datetime, Field(description="Date record was updated last")]
    
    @field_serializer("id")
    def serialize_id(self, v: UUID) -> str: 
        return str(v)
    
    @field_serializer("dataset_id")
    def serialize_dataset_id(self, v: UUID) -> str: 
        return str(v)
    
class RecordResponse(BaseResponse):
    data: Annotated[RecordResponseSchema, Field(description="Record data")]
    

class RecordListResponse(BaseResponse):
    data: Annotated[list[RecordResponseSchema], Field(description="List of Record data response")]
    
class RecordPaginatedResponseSchema(BasePaginatedResponseSchema):
    records: Annotated[list[RecordResponseSchema], Field(description="List of records for dataset")]
    
class RecordPaginatedRespone(BaseResponse):
    data: Annotated[RecordPaginatedResponseSchema, Field(description="Paginated Record data")]
    

class BatchUpdate(BaseModel):
    id: Annotated[UUID, Field(description="Id of the record to update")]
    data: Annotated[dict[str, Any], Field(description="Fields to update")]

    @field_serializer("id")
    def serialize_id(self, v: UUID) -> str: 
        return str(v)
    
class ListBatchUpdate(BaseModel):
    records: Annotated[list[BatchUpdate], Field(description="List of records to update")]
    