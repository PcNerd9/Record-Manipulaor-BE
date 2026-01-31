from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, status
from datetime import datetime, timezone

from app.crud.crud_user import crud_users
from app.core.exceptions.http_exceptions import DuplicateValueException, NotFoundException, ForbiddenException
from app.schemas.user import UserCreate, UserCreateInternals, UserUpdate, UserRead
from app.model.user import OTPType, User
from app.core.security import generate_otp, hash_password
from app.core.utils.email import send_otp_verification_email
from app.core.response import response_builder


class UserService:
    async def create_user(self, user_data: UserCreate, db: AsyncSession, background_task: BackgroundTasks) -> dict[str, Any]:
        
        email_row = await crud_users.exists(db=db, email=user_data.email)
        if email_row:
            raise DuplicateValueException("Email is already registerd")
        
        user_internal_dict = user_data.model_dump()
        user_internal_dict["password"] = hash_password(user_data.password.get_secret_value())
        
        otp = generate_otp(6)
        user_internal_dict["otp"] = hash_password(otp)
        user_internal_dict["otp_expiry"] = datetime.now(timezone.utc)
        user_internal_dict["otp_type"] = OTPType.EMAIL_VERIFICATION
        
        user_internal = UserCreateInternals(**user_internal_dict)
        created_user = await crud_users.create(db=db, object=user_internal, schema_to_select=UserRead)
        
        #send email
        background_task.add_task(
            send_otp_verification_email,
            email_to=created_user["email"],
            first_name=created_user["first_name"],
            otp_code=created_user["otp"]
        )
        
        return response_builder(
            status_code=status.HTTP_201_CREATED,
            status="success",
            message="User created successfully, Otp sent to email for verification"
        )
        
    async def current_user(self, user: User) -> dict[str, Any]:
        pass
    
    
user_service = UserService()