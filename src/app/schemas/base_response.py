from pydantic import BaseModel, Field
from typing import Annotated


class BaseResponse(BaseModel):
    status_code: Annotated[int, Field(description="Response status code", examples=[200])]
    status: Annotated[str, Field(description="Status of response success/fail", examples=["success", "fail"])]
    message: Annotated[str, Field(description="Response Message", examples=["user fetch successfully"])]
    
class PaginatedMetadata(BaseModel):
    page_size: Annotated[int, Field(ge=1, le=100, description="number of resources per page", examples=["20"])]
    page: Annotated[int, Field(ge=1, description="page to fetch", examples=["20"])]
    total: Annotated[int, Field(description="Total number of resources", examples=["20"])]
    total_page: Annotated[int, Field(description="number of pages resource has", examples=["20"])]
    has_next_page: Annotated[bool, Field(description="Indicate whether recourse has next page", examples=[True])]
    has_prev_page: Annotated[bool, Field(description="Indicate whether recourse has prev page", examples=[False])]
    
class BasePaginatedResponseSchema(BaseModel):
    meta: Annotated[PaginatedMetadata, Field(description="Paginated metadata")]