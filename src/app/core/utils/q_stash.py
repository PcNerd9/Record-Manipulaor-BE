from qstash import QStash
from datetime import timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis import redis_client
from app.model.task import Task


qstash = QStash(token=settings.QSTASH_TOKEN)

def enqueue_image_job(payload: dict, type: str):
    
    base_url = f"{settings.APP_URL}/api/v1/jobs/execute"
    
    if type == "upload": 
        base_url = f"{base_url}/upload-dataset"
    elif type == "download":
        base_url = f"{base_url}/download-dataset"
    
    res = qstash.message.publish_json(
        url=base_url,
        body=payload,
        retries=3,
        delay=0
    )
    print(res)
    

async def save_job_state(
    job_id: str,
    status: str
):
    redis_client.setex(job_id, timedelta(hours=1), status)
    
    

async def update_job_state(
    job_id: str,
    status: str,
    db: Session,
    data: dict | None = None
):    
    redis_client.setex(job_id, timedelta(hours=1), status)
    
    if status in ["completed", "failed"]:
        task = await Task.get_by_unique(key="job_id", value=job_id, db=db)
        if task:
            
            await task.update({"status":status, "result":data}, db)
        else:
            task_data = {"job_id": job_id, "status": status, "result": data}
            await Task.create(data=task_data, db=db)
    
    
async def get_job_state(
    job_id: str,
    db: Session
):
    status = redis_client.get(job_id)

    result = None
    if status in ["completed", "failed"]:
        result = await Task.get_by_unique(key="job_id", value=job_id, db=db)
    
    return result if result else {"status": status, "data": "No data"}