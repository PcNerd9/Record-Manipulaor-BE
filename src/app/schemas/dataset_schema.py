from pydantic import BaseModel, Field
from typing import Annotated, Any
from uuid import UUID
from datetime import datetime

from app.schemas.base_response import BaseResponse, BasePaginatedResponseSchema


    
    
class DatasetResponseSchema(BaseModel):
    id: Annotated[UUID, Field(description="Dataset Id", examples=["1234-33ddh-dhdh-33esd-3303"])]
    user_id: Annotated[UUID, Field(description="Id of the user that owns the dataset", examples=["1234-33ddh-dhdh-33esd-3303"])]
    name: Annotated[str, Field(description="The name of the file")]
    data_schema: Annotated[dict[str, Any], Field(description="The Columns of the dataset")]
    created_at: Annotated[datetime, Field(description="When user was created", examples=["2026-01-20"])]
    updated_at: Annotated[datetime, Field(description="When User was updated last", examples=["2026-01-23"])]
    

class DatasetResponse(BaseResponse):
    data: Annotated[DatasetResponseSchema, Field(description="Dataset Data")]
    
    
class DatasetPaginatedResponseSchema(BasePaginatedResponseSchema):
    datasets: Annotated[list[DatasetResponseSchema], Field(description="List of datasets")]

class DatasetPaginatedResponse(BaseResponse):
    data: Annotated[DatasetPaginatedResponseSchema, Field(description="dataset data")]
    
    

    
    
    