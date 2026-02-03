from pydantic import BaseModel, EmailStr, ConfigDict, Field, SecretStr, field_serializer
from typing import Annotated
from uuid import UUID
from datetime import datetime
from enum import Enum

from app.model.user import OTPType
from app.schemas.base_response import BaseResponse

class UserBase(BaseModel): 
    first_name: Annotated[str, Field(description="User first name", examples=['John'])]
    last_name: Annotated[str, Field(description="User Last Name", examples=["Doe"])]
    email: Annotated[EmailStr, Field(description="User email", examples=["johndoe@example.com"])]

    
class UserCreate(UserBase):
    password: Annotated[SecretStr, Field(
        description="User password", 
        examples=["johnexample"],
        min_length=8,
        max_length=64
    )]
    
    model_config = ConfigDict(extra="forbid")
    
class UserResponseSchema(UserBase):
    is_active: Annotated[bool, Field(description="True if user is active otherwise False", default=True)]
    id: Annotated[UUID, Field(description="User Id", examples=["1234-33ddh-dhdh-33esd-3303"])]
    created_at: Annotated[datetime, Field(description="When user was created", examples=["2026-01-20"])]
    updated_at: Annotated[datetime, Field(description="When User was updated last", examples=["2026-01-23"])]
    
class UserReadInternal(UserRead):
    password: Annotated[str, Field(description="User Hashed Password")]
    is_deleted: Annotated[bool, Field(description="Is user Deleted soft delete", default=False)]
    deleted_at: Annotated[datetime | None, Field(description="When user get deleted (soft delete)", default=None)]
    
    otp: Annotated[str | None, Field(description="Otp for verification", default=None)]
    otp_type: Annotated[OTPType | None, Field(description="The Type of the Otp", default=None, examples=[OTPType.EMAIL_VERIFICATION.value])]
    otp_expiry: Annotated[datetime | None, Field(description="When otp will expire", default=None)]

    
    @field_serializer("id")
    def serialize_id(self, v: UUID) -> str: 
        return str(v)
    
    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, v: datetime) -> str:
        return v.isoformat()
    
    
class UserUpdate(BaseModel):
    first_name: Annotated[str, Field(description="User first nanem", examples=["John"])]
    last_name: Annotated[str, Field(description="User last name", examples=["Doe"])]

    model_config = ConfigDict(extra="forbid")
    
    
class Userfilter(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    
class UUIDSchema(BaseModel):
    id: UUID
    
class UserResponse(BaseResponse):
    data: Annotated[UserResponseSchema, Field(description="User created data")]