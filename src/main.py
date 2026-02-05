from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import structlog

from app.api.v1 import api_router
from app.core.config import settings
from app.core.health import check_database_health, check_redis_health
from app.core.db.database import async_get_db, async_engine
from app.core.redis import  get_redis, init_redis


logger = structlog.get_logger(__name__)

@asynccontextmanager
async def fastapi_lifespan(app: FastAPI):
    
    gen =  async_get_db()
    db = await anext(gen)
    
    if await check_database_health(db):
        logger.info("✅ Database working properly")
        
    try:
        await init_redis()
        redis = await get_redis()
        if await check_redis_health(redis):
            logger.info("✅ Redis working properly")
    except RuntimeError as e:
        logger.exception(f"❌ {str(e)}")
        
    yield
    
    await async_engine.dispose()
    logger.info("✅ successfully shutdown postgres engine")
    
def custom_generator_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"
    
    
app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_BASE}/openapi.json",
    generate_unique_id_function=custom_generator_unique_id,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTON,
    lifespan=fastapi_lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
    allow_credentials=True
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    
    logger.exception(str(exc))
    
    message = str(exc) if settings.ENVIRONMENT == "local" else "Internal server Error"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "status": "error",
            "message": message
        }
    )
    
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT)