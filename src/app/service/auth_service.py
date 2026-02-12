from fastapi import status, BackgroundTasks
from fastapi.requests import Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from app.model.user import User, OTPType
from app.model.refresh_token import RefreshToken
from app.core.security import create_access_token, create_refresh_token, set_cookeies, verify_pasword, hash_token, verify_hash_token
from app.core.response import response_builder
from app.core.exceptions.http_exceptions import NotFoundException, UnauthorizedException, BadRequestException
from app.core.config import settings
from app.core.utils.email import send_otp_verification_email
from app.core.security import hash_password, generate_otp, verify_token, TokenType, blacklist_token, delete_cookies

class AuthService:
    async def login_user(self, login_data: dict[str, Any], db: AsyncSession, request: Request, response: Response) -> dict[str, Any]:
        user = await User.get_by_unique(key="email", value=login_data["email"].lower(), db=db)
        if not user:
            raise UnauthorizedException("User Not Found")
        
        if not verify_pasword(
            login_data["password"].get_secret_value(),
            user.password
        ):
            raise UnauthorizedException("Wrong password")
        
        # Get Request Metada
        device_id = request.cookies.get("device_id", None)
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        access_token = create_access_token(str(user.id))
        
        # Geenerate new device id if None
        new_device_id = device_id if device_id else str(uuid4())
        
        refresh_token, jti = create_refresh_token(str(user.id))
        hashed_refresh_token = hash_token(refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Check if there is already a session for that user and the device, if yes revoke it
        # This is to ensure only one session per user and device_id
        token = await RefreshToken.get_token_by_user_and_device_id(str(user.id), new_device_id, db)
        if token:
            await token.revoke(db)
        
        
        await RefreshToken.create_refresh_token(
            user_id=str(user.id),
            token=hashed_refresh_token,
            device_id=new_device_id,
            jti=jti,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            db=db
        )

        max_age = int(expires_at.timestamp())
        
        if not device_id:
            set_cookeies(
                response, "device_id", new_device_id, max_age=31536000
            ) # Setting the device_id cookie to 1 year
            

        set_cookeies(response, "refresh_token", refresh_token, max_age)
        
        user_data = user.to_dict()
        
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="User logged in successfully",
            data={
                "user": user_data,
                "access_token": access_token
            }
        )
        
    
    async def resend_email_verification_otp(
        self,
        email: str,
        db: AsyncSession,
        background_task: BackgroundTasks
    ) -> dict[str, Any]:
        
        user = await User.get_by_unique(key="email", value=email.lower(), db=db)
        if not user:
            raise NotFoundException("Email has not been registered")
        
        otp = generate_otp(6)
        hashed_otp = hash_password(otp)
        user.otp = hashed_otp
        
        user.otp_type = OTPType.EMAIL_VERIFICATION
        user.otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_TIME)
        await user.save(db)
        
        background_task.add_task(
            send_otp_verification_email,
            email_to=user.email,
            first_name=user.first_name,
            otp_code=otp
        )
        
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="Email is sent successfully"
        ) 
        
    async def verify_email(self, email: str, otp: str, db: AsyncSession) -> dict[str, Any]:
        user = await User.get_by_unique(key="email", value=email.lower(), db=db)
        print(email.lower())
        if not user:
            raise NotFoundException("Email not registered")
        
        if (
            not user.otp 
            or not user.otp_expiry 
            or user.otp_expiry >= datetime.now(timezone.utc)
            or not user.otp_type
            or user.otp_type != OTPType.EMAIL_VERIFICATION
        ):
            raise BadRequestException("Invalid otp")

        if not verify_pasword(otp, user.otp):
            raise UnauthorizedException("Invalid otp")
        
        user.otp = None
        user.otp_expiry = None
        user.otp_type = None
        
        user.is_verified = True
        await user.save(db)
        
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="succcess",
            message="Email verified successfully"
        )
        
    async def logout(
        self,
        user: User,
        request: Request,
        db: AsyncSession, 
        response: Response
    ) -> dict[str, Any]:
        
        auth_token = request.headers.get("Authorization")
        if not auth_token or not auth_token.startswith("Bearer "):
            raise UnauthorizedException("Invalid authorization header")
        
        auth_token = auth_token.split(" ")[1]
        
        await blacklist_token(auth_token)     
          
        # Get device_id and refresh token from cookies
        device_id = request.cookies.get("device_id", None)
        refresh_token = request.cookies.get("refresh_token", None)
        
        if refresh_token:            
            delete_cookies(response, "refresh_token")  
            
        if device_id:
            token = await RefreshToken.get_token_by_user_and_device_id(str(user.id), device_id, db)
            
            # If not token, then user might be compromised, so clear device_id
            if not token:
                delete_cookies(response, "device_id")
            else:
                await token.revoke(db)
            
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="User Logged out successfully"
        )
        
        
    async def refresh_token(
        self,
        request: Request,
        response: Response,
        db: AsyncSession
    ):
        
        refresh_token = request.cookies.get("refresh_token")
        device_id = request.cookies.get("device_id")
        user_agent = request.headers.get("user-agent", "unknown")
        ip_address = request.client.host if request.client else "unknown"

        if not refresh_token or not device_id:
            raise UnauthorizedException("No refresh token or devce id provided")
        
        refresh_token_payload = await verify_token(refresh_token, TokenType.REFRESH)
        if not refresh_token_payload:
            raise UnauthorizedException("Invalid refresh token")
        
        jti = refresh_token_payload.get("jti")
        user_id = refresh_token_payload.get("sub")
        type = refresh_token_payload.get("type")
        
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")
        
        if not type or type != TokenType.REFRESH:
            raise UnauthorizedException("Invalid token Type")
        
        user = await User.get_by_id(user_id, db)
        if not user:
            raise UnauthorizedException("Could not validate credentials")
        
        token = await RefreshToken.get_token_by_user_and_device_id(user_id, device_id, db)
        if not token:
            raise BadRequestException("No Session for this device")
        
        if token.jti != jti:
            raise UnauthorizedException("Invalid refresh token")
        
        if token.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedException("Session expired")

        
        await token.revoke(db)
        
        new_refresh_token, jti = create_refresh_token(str(user.id))
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        await RefreshToken.create_refresh_token(
            user_id=str(user.id),
            token=new_refresh_token,
            device_id=device_id,
            jti=jti,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
            db=db,
        )
        
        max_age = max_age = int((expires_at - datetime.now(timezone.utc)).total_seconds())
        
        set_cookeies(response, "refresh_token", new_refresh_token, max_age)
        
        access_token = create_access_token(str(user.id))
        
        return response_builder(
            status_code=status.HTTP_200_OK,
            status="success",
            message="successfully generate access token",
            data={"access_token": access_token}
        )

            
                
auth_service = AuthService()
            
        
        
        