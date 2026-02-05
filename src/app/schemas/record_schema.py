from pydantic import Field, BaseModel
from typing import Any, Annotated
from uuid import UUID

from app.schemas.base_response import BaseResponse, BasePaginatedResponseSchema


class RecordBase(BaseModel):
    data: Annotated[dict[str, Any], Field(description="A Json of the column where key is the column name and value is the value for that column")]
    
class RecordCreate(RecordBase):
    ...

class RecordUpdate(RecordBase):
    ...

class RecordResponseSchema(RecordBase):
    dataset_id: Annotated[UUID, Field(description="Dataset id the record belong to")]
    
class RecordResponse(BaseResponse):
    data: Annotated[RecordResponseSchema, Field(description="Record data")]
    

class RecordListResponse(BaseResponse):
    data: Annotated[list[RecordResponseSchema], Field(description="List of Record data response")]
    
class RecordPaginatedResponseSchema(BasePaginatedResponseSchema):
    records: Annotated[RecordResponseSchema, Field(description="List of records for dataset")]
    
class RecordPaginatedRespone(BaseResponse):
    data: Annotated[RecordPaginatedResponseSchema, Field(description="Paginated Record data")]