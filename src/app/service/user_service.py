from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, status
from datetime import datetime, timezone, timedelta

from app.core.exceptions.http_exceptions import ConflictException
from app.model.user import OTPType, User
from app.core.security import generate_otp, hash_password
from app.core.config import settings
from app.core.utils.email import send_otp_verification_email
from app.core.response import response_builder


class UserService:
    async def create_user(self, user_data: dict[str, Any], db: AsyncSession, background_task: BackgroundTasks) -> dict[str, Any]:
        
        user_data["email"] = user_data["email"].lower()
        user = await User.get_by_unique(key="email", value=user_data["email"], db=db)
        if user:
            raise ConflictException("Email is already registerd")
        
        user_data["password"] = hash_password(user_data["password"].get_secret_value())
        
        otp = generate_otp(6)
        user_data["otp"] = hash_password(otp)
        user_data["otp_expiry"] = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_TIME)
        user_data["otp_type"] = OTPType.EMAIL_VERIFICATION
  
        created_user = await User.create(data=user_data, db=db)
        
        #send email
        background_task.add_task(
            send_otp_verification_email,
            email_to=created_user.email,
            first_name=created_user.first_name,
            otp_code=otp
        )
        
        return response_builder(
            status_code=status.HTTP_201_CREATED,
            status="success",
            message="User created successfully, Otp sent to email for verification"
        )
        
    async def current_user(self, user: User) -> dict[str, Any]:
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="successfully fetch current user",
            data=user.to_dict()
        )
    
    
user_service = UserService()