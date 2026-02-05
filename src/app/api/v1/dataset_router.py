from fastapi import APIRouter, status, UploadFile, Query

from app.api.dependencies import dbDepSession, ActiveCurrentUser, fileDep
from app.service.dataset_service import dataset_service
from app.service.record_service import record_service
from app.schemas.dataset_schema import DatasetResponse, DatasetPaginatedResponse, BaseResponse
from app.schemas.record_schema import RecordCreate, RecordResponse, RecordPaginatedRespone, RecordUpdate, RecordListResponse



dataset = APIRouter(
    prefix="/dataset",
    tags=["Dataset"]
)

@dataset.post(
    "/upload",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
    description="Upload Dataset file. supported format are .csv, .xls and .xlxs"
)
async def upload_dataset(
    file: fileDep,
    db: dbDepSession,
    user: ActiveCurrentUser
):
    return await dataset_service.create_dataset(db, file, user.id)

@dataset.post(
    "/{id}/records",
    response_model=RecordResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new record in the dataset"
)
async def create_record(
    id: str,
    record_data: RecordCreate,
    db: dbDepSession,
    user: ActiveCurrentUser
):
    return await record_service.create_record(db, id, user, record_data.model_dump())


@dataset.get(
    "/",
    response_model=DatasetPaginatedResponse,
    status_code=status.HTTP_200_OK,
    description="Get all the dataset for a user"
)
async def get_dataset_by_user(
    db: dbDepSession,
    user: ActiveCurrentUser,
    name: str | None = Query(default=None, description="Filter by name of dataset"),
    page: int | None = Query(default=1, ge=1, description="The page to fetch"),
    page_size: int | None = Query(default=10, ge=1, description='Number of resources per page')
):
    return await dataset_service.get_dataset_by_user(db, user, name, page, page_size)


@dataset.get(
    "/{id}/export",
    description="Export a dataset into csv or xlxs"
)
async def export_dataset(
    id: str,
    db: dbDepSession,
    user: ActiveCurrentUser,
    format: str | None = Query(default="csv", description="The format to export as", examples=["csv", "xlxs"])
):
    await dataset_service.export_dataset(id, db, user)
    

@dataset.get(
    "/{id}/records",
    response_model=RecordPaginatedRespone,
    status_code=status.HTTP_200_OK,
    description="Fetch all records in a dataset paginated"
    
)
async def get_all_record_for_dataset(
    id: str,
    db: dbDepSession,
    user: ActiveCurrentUser,
    page: int = Query(default=1, ge=1, le=1, examples=["2"], description="The current page to fetch"),
    page_size: int = Query(default=10, ge=1, examples=["50"], description="Number of resource to fetch per page")
):
    return await record_service.get_records_for_dataset(id, user, db, page, page_size)


@dataset.get(
    "/{id}/records/filter",
    response_model=RecordListResponse,
    status_code=status.HTTP_200_OK,
    description="Filter records by using column"
)
async def filter_rows_by_column(
    id: str,
    db: dbDepSession,
    user: ActiveCurrentUser,
    key: str = Query(description="Name of the column to filter by"),
    value: str = Query(description="Value of the column for filtering"),
    limit: int = Query(default=100, ge=1, description="Number of records to fetch")
):
    return await record_service.filter_record_by_column(id, key, value, db, user, limit)

@dataset.get(
    "/{id}",
    response_model=DatasetResponse,
    status_code=status.HTTP_200_OK,
    description="Fetch Dataset by Id"
)
async def get_dataset_by_id(
    id: str,
    db: dbDepSession,
    user: ActiveCurrentUser
):
    return await dataset_service.get_dataset(id, user, db)


@dataset.put(
    "/records/{record_id}",
    response_model=RecordResponse,
    status_code=status.HTTP_200_OK,
    description="Update record of a dataset"
)
async def update_record(
    record_id: str,
    record_data: RecordUpdate,
    db: dbDepSession,
    user: ActiveCurrentUser
):
    return await record_service.update_record(record_id, record_data.model_dump(), db, user)


@dataset.delete(
    "/record/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a record"
)
async def delete_record(
    record_id: str,
    user: ActiveCurrentUser,
    db: dbDepSession
):
    return await record_service.delete_record(record_id, user, db)


@dataset.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete dataset"
)
async def delete_dataset(
    id: str,
    db: dbDepSession,
    user: ActiveCurrentUser
):
    return await dataset_service.delete_dataset(user, id, db)



