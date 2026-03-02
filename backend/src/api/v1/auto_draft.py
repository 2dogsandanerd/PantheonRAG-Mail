from src.core.rate_limiter import limiter, RATE_LIMITS
from src.database.models import User
from fastapi import Request, APIRouter, Depends

from src.api.v1.dependencies import get_auto_draft_service
from src.services.auto_draft_service import AutoDraftService
from src.core.auth import get_current_active_user

router = APIRouter()


@router.post("/start")
@limiter.limit(RATE_LIMITS["default"])
async def start_auto_draft(request: Request, 
    current_user: User = Depends(get_current_active_user),
    service: AutoDraftService = Depends(get_auto_draft_service)
):
    """Start auto-draft monitoring service"""
    # In a real async setup, this would likely trigger a persistent task.
    # For now, we use the service's state.
    success = await service.start_monitoring()

    if not success:
        return {
            "status": "already_running",
            "message": "Auto-draft service is already running."
        }

    status = await service.get_status()
    return {
        "status": "started",
        "interval": status.get("interval"),
        "worker_id": status.get("worker_id")
    }


@router.post("/stop")
@limiter.limit(RATE_LIMITS["default"])
async def stop_auto_draft(request: Request, 
    current_user: User = Depends(get_current_active_user),
    service: AutoDraftService = Depends(get_auto_draft_service)
):
    """Stop auto-draft monitoring service"""
    await service.stop_monitoring()
    return {"status": "stopped"}


@router.get("/status")
@limiter.limit(RATE_LIMITS["default"])
async def get_status(request: Request, 
    current_user: User = Depends(get_current_active_user),
    service: AutoDraftService = Depends(get_auto_draft_service)
):
    """Get auto-draft service status"""
    return await service.get_status()