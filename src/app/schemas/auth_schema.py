from pydantic import BaseModel, Field, SecretStr, EmailStr
from typing import Annotated
from app.schemas.user import UserResponseSchema
from app.schemas.base_response import BaseResponse

class LoginUser(BaseModel):
    email: Annotated[EmailStr, Field(description="User email", examples=["johndoe@example.com"])]
    password: Annotated[SecretStr, Field(description="User Password", examples=["johndoe123222!"])]

class RegenerateOTP(BaseModel):
    email: Annotated[EmailStr, Field(description="User email", examples=["johndoe@example.com"])]
    
class EmailVerification(BaseModel):
    email: Annotated[EmailStr, Field(description="User email", examples=["johndoe@example.com"])]
    otp: Annotated[str, Field(description="User otp", examples=["093232!"])]
    
class LoginUserResponseSchema(BaseModel):
    user: Annotated[UserResponseSchema, Field(description="User data")]
    access_token: Annotated[str, Field(description="Access token")]
    
class LoginUserResponse(BaseResponse):
    data: Annotated[LoginUserResponseSchema, Field(description="User login data")]
    
class RefreshTokenResponseSchema(BaseModel):
    access_token: Annotated[str, Field(description="User new access token")]
    
class RefreshTokenResponse(BaseResponse):
    data: Annotated[RefreshTokenResponseSchema, Field(description="User new access token")]