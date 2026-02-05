from fastapi import APIRouter, status, BackgroundTasks
from fastapi.requests import Request
from fastapi.responses import Response

from app.api.dependencies import dbDepSession, currentUser

from app.schemas.auth_schema import LoginUser, RegenerateOTP, EmailVerification, LoginUserResponse, RefreshTokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.schemas.base_response import BaseResponse

from app.service.auth_service import auth_service
from app.service.user_service import user_service

auth = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@auth.post(
    "/create-user",
    summary="Create a new user",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponse
)
async def create_user(
    db: dbDepSession,
    user_data: UserCreate,
    background_task: BackgroundTasks
):
    return await user_service.create_user(
        user_data=user_data.model_dump(), 
        db=db, 
        background_task=background_task
    )
    

@auth.post(
    "/login",
    summary="Login user",
    status_code=status.HTTP_200_OK,
    response_model=LoginUserResponse
)
async def login_user(
    db: dbDepSession,
    login_data: LoginUser,
    request: Request,
    response: Response
):
    return await auth_service.login_user(
        login_data=login_data.model_dump(),
        db=db,
        request=request,
        response=response
    )
    
@auth.post(
    "/resend-otp",
    summary="Resend OTP",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK
)
async def resend_otp(
    db: dbDepSession,
    otp_data: RegenerateOTP,
    background_task: BackgroundTasks
):
    return await auth_service.resend_email_verification_otp(otp_data.email, db, background_task=background_task)

@auth.post(
    "/verify-email",
    summary="Verify user email",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK
)
async def verify_email(
    db: dbDepSession,
    email_data: EmailVerification,
):
    return await auth_service.verify_email(email_data.email, email_data.otp, db)

@auth.post(
    "/refresh-token",
    summary="Get a new access token using your refresh token",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK
)
async def refresh_token(
    user: currentUser,
    request: Request,
    response: Response,
    db: dbDepSession
):
    return await auth_service.refresh_token(
        user,
        request,
        response,
        db
    )
    
@auth.post(
    "/logout",
    summary="Logout user",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK
)
async def logout_user(
    user: currentUser,
    request: Request,
    response: Response,
    db: dbDepSession
):
    return await auth_service.logout(user, request, db, response)