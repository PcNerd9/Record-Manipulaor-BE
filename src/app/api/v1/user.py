from fastapi import APIRouter, status

from app.service.user_service import user_service
from app.schemas.user import UserResponse
from app.api.dependencies import currentUser


user = APIRouter(
    prefix="/user",
    tags=["User"]
)

@user.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    description="get current logged in user"
)
async def get_current_user(
    user: currentUser
):
    return await user_service.current_user(user)