from src.api.v1.deps import CurrentUser
from src.core.auth import get_current_active_user
from src.database.models import User
from fastapi import APIRouter, HTTPException, Depends
from celery.result import AsyncResult
from src.workers.celery_app import celery_app
from typing import Optional, Any
from pydantic import BaseModel

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: Optional[int] = None

@router.get("/")
async def list_tasks(current_user: CurrentUser):
    """List active and reserved tasks from Celery workers."""
    try:
        i = celery_app.control.inspect()
        active = i.active() or {}
        reserved = i.reserved() or {}
        scheduled = i.scheduled() or {}

        # Flatten and format
        tasks = []
        for worker, task_list in active.items():
            for task in task_list:
                task["status"] = "ACTIVE"
                task["worker"] = worker
                tasks.append(task)
        for worker, task_list in reserved.items():
            for task in task_list:
                task["status"] = "RESERVED"
                task["worker"] = worker
                tasks.append(task)
        for worker, task_list in scheduled.items():
            for task in task_list:
                task["status"] = "SCHEDULED"
                task["worker"] = worker
                tasks.append(task)
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to inspect tasks: {str(e)}")

@router.get("/{task_id}")
async def get_task_status(task_id: str, current_user: CurrentUser):
    """Get the status of a specific task."""
    task_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
    }

@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str, current_user: CurrentUser):
    """Cancel a running task."""
    task_result = AsyncResult(task_id, app=celery_app)
    task_result.revoke(terminate=True)
    return {"message": f"Task {task_id} cancelled"}
