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
    row_count: Annotated[int, Field(description="Number of rows in dataset", examples=["1000"])]
    column_count: Annotated[int, Field(description="Number of columns in dataset", examples=["10"])]
    created_at: Annotated[datetime, Field(description="When user was created", examples=["2026-01-20"])]
    updated_at: Annotated[datetime, Field(description="When User was updated last", examples=["2026-01-23"])]
    
class DatasetUploadResponseSchema(BaseModel):
    dataset_id: Annotated[UUID, Field(description="newly created dataset id")]
    dataset_name: Annotated[str, Field(description="The name of the dataset")]
    rows: Annotated[int, Field(description="the number of rows in a dataset")]
    columns: Annotated[list[str], Field(description="the list of columns the dataset has")]


class DatasetUploadResponse(BaseResponse):
    data: Annotated[DatasetUploadResponseSchema, Field(description="Dataset Upload response data")]

class DatasetResponse(BaseResponse):
    data: Annotated[DatasetResponseSchema, Field(description="Dataset Data")]
    
    
class DatasetPaginatedResponseSchema(BasePaginatedResponseSchema):
    datasets: Annotated[list[DatasetResponseSchema], Field(description="List of datasets")]

class DatasetPaginatedResponse(BaseResponse):
    data: Annotated[DatasetPaginatedResponseSchema, Field(description="dataset data")]
    
class UpdateDataset(BaseModel):
    name: Annotated[str, Field(description="The name of the file")]
    
    

    
    
    