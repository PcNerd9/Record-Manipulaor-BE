from pydantic import BaseModel, Field
from typing import Annotated


class BaseResponse(BaseModel):
    status_code: Annotated[int, Field(description="Response status code", examples=[200])]
    status: Annotated[str, Field(description="Status of response success/fail", examples=["success", "fail"])]
    message: Annotated[str, Field(description="Response Message", examples=["user fetch successfully"])]
    

class BasePaginatedResponseSchema(BaseModel):
    page_size: Annotated[int, Field(ge=1, le=100, description="number of resources per page", examples=["20"])]
    page_size: Annotated[int, Field(ge=1, description="page to fetch", examples=["20"])]
    page_size: Annotated[int, Field(description="Total number of resources", examples=["20"])]