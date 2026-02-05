from fastapi import APIRouter

from app.api.v1.auth_router import auth
from app.api.v1.user import user
from app.api.v1.dataset_router import dataset

from app.core.config import settings

api_router = APIRouter(prefix=settings.API_BASE)

api_router.include_router(auth)
api_router.include_router(user)
api_router.include_router(dataset)