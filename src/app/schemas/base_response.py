from pydantic import BaseModel, Field
from typing import Annotated


class BaseResponse(BaseModel):
    status_code: Annotated[int, Field(description="Response status code", examples=[200])]
    status: Annotated[str, Field(description="Status of response success/fail", examples=["success", "fail"])]
    message: Annotated[str, Field(description="Response Message", examples=["user fetch successfully"])]