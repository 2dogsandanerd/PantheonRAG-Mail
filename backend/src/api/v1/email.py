from src.core.rate_limiter import limiter, RATE_LIMITS
from src.database.models import User
from src.core.exceptions import ValidationError, ServiceUnavailableError, DocumentNotFoundError
from fastapi import Request, APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.api.v1.dependencies import (
    get_email_client,
    get_draft_service,
    get_learning_manager
)
from src.core.auth import get_current_active_user
from src.core.email_clients.base_client import AbstractEmailClient
from src.services.draft_service import DraftService
from src.services.learning_manager import LearningManager

# ... [Pydantic models remain the same] ...

class EmailResponse(BaseModel):
    emails: List[Dict[str, Any]]
    count: int
    user_id: int
    configured: bool
    message: Optional[str] = None

class ThreadResponse(BaseModel):
    thread: List[Dict[str, Any]]
    thread_id: str

class DraftRequest(BaseModel):
    sender: str
    subject: str
    body: str
    thread_id: str
    use_rag: bool = True

class DraftResponse(BaseModel):
    draft: Optional[str] = None
    no_answer_needed: bool
    reason_category: Optional[str] = None
    reason_text: Optional[str] = None
    rag_context: Optional[str] = None
    model: Optional[str] = None
    rag_status: Optional[str] = None
    rag_error: Optional[str] = None
    rag_collection_count: Optional[int] = None
    rag_result_count: Optional[int] = None
    draft_id: Optional[int] = None
    already_existed: Optional[bool] = None
    status: Optional[str] = None
    conversation_id: Optional[str] = None

class SaveDraftRequest(BaseModel):
    to: str
    subject: str
    body: str
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    source_folder: Optional[str] = None

class SaveDraftResponse(BaseModel):
    draft_id: str
    status: str
    provider: str
    learning_pair_id: Optional[int] = None

class ClearInboxResponse(BaseModel):
    success: bool
    count: int
    message: str

class DraftListResponse(BaseModel):
    drafts: List[Dict[str, Any]]

class DeleteDraftResponse(BaseModel):
    success: bool
    message: str

router = APIRouter()

@router.get("/inbox", response_model=EmailResponse)
@limiter.limit(RATE_LIMITS["email"])
async def get_inbox(request: Request, 
    max_results: int = 10,
    filter_mode: str = "none",
    draft_service: DraftService = Depends(get_draft_service),
    client: AbstractEmailClient = Depends(get_email_client),
    current_user: User = Depends(get_current_active_user)
):
    try:
        emails = await client.get_unread_emails(max_results=max_results)
        
        if filter_mode == "auto":
            filtered_result = await draft_service.filter_emails_batch(
                email_list=emails,
                user_id=current_user.id
            )
            emails = filtered_result["draft_needed_emails"]

        return EmailResponse(
            emails=emails,
            count=len(emails),
            user_id=current_user.id,
            configured=True
        )
    except HTTPException as e:
        # Re-raise HTTPException to let FastAPI handle it
        raise e
    except Exception as e:
        raise ServiceUnavailableError("email", str(e))

@router.get("/thread/{thread_id}", response_model=ThreadResponse)
@limiter.limit(RATE_LIMITS["email"])
async def get_thread_history(request: Request, 
    thread_id: str,
    client: AbstractEmailClient = Depends(get_email_client),
    current_user: User = Depends(get_current_active_user)
):
    try:
        thread = await client.get_thread_history(thread_id)
        return ThreadResponse(thread=thread, thread_id=thread_id)
    except Exception as e:
        raise DocumentNotFoundError(str(e), collection="email_thread")

@router.post("/draft", response_model=DraftResponse)
@limiter.limit(RATE_LIMITS["email"])
async def generate_draft(request: Request, 
    draft_request: DraftRequest,
    draft_service: DraftService = Depends(get_draft_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        email_data = draft_request.dict()
        result = await draft_service.generate_draft_with_learning(
            email_data=email_data,
            user_id=current_user.id,
            thread_id=draft_request.thread_id,
            use_rag=draft_request.use_rag
        )
        return result
    except Exception as e:
        raise ServiceUnavailableError("email", str(e))

@router.post("/draft/save", response_model=SaveDraftResponse)
@limiter.limit(RATE_LIMITS["email"])
async def save_draft_to_provider(request: Request, 
    save_request: SaveDraftRequest,
    client: AbstractEmailClient = Depends(get_email_client),
    learning_manager: LearningManager = Depends(get_learning_manager),
    current_user: User = Depends(get_current_active_user)
):
    try:
        draft_id = await client.create_draft(
            to=save_request.to,
            subject=save_request.subject,
            body=save_request.body,
            thread_id=save_request.thread_id,
            in_reply_to=save_request.in_reply_to
        )
        if not draft_id:
            raise ServiceUnavailableError("email_provider", "Failed to create draft")

        learning_pair_id = await learning_manager.add_draft(
            user_id=current_user.id,
            thread_id=save_request.thread_id or draft_id,
            draft_message_id=draft_id,
            draft_content=save_request.body
        )

        if save_request.source_folder and save_request.in_reply_to:
            await client.remove_label_from_email(
                message_id=save_request.in_reply_to,
                folder_or_label_name=save_request.source_folder
            )

        return SaveDraftResponse(
            draft_id=draft_id,
            status="created",
            provider=client.__class__.__name__,
            learning_pair_id=learning_pair_id
        )
    except Exception as e:
        raise ServiceUnavailableError("email", str(e))

@router.post("/clear-inbox", response_model=ClearInboxResponse)
@limiter.limit(RATE_LIMITS["email"])
async def clear_inbox(request: Request, 
    client: AbstractEmailClient = Depends(get_email_client),
    current_user: User = Depends(get_current_active_user)
):
    try:
        result = await client.clear_inbox()
        if result.get("status") == "success":
            return ClearInboxResponse(
                success=True, 
                count=result.get("count", 0), 
                message=result.get("message", "Inbox cleared.")
            )
        else:
            raise ServiceUnavailableError("email", result.get("message", "Unknown error"))
    except Exception as e:
        raise ServiceUnavailableError("email", str(e))

@router.get("/drafts", response_model=DraftListResponse)
@limiter.limit(RATE_LIMITS["email"])
async def get_drafts(request: Request, 
    status: Optional[str] = None,
    limit: int = 50,
    learning_manager: LearningManager = Depends(get_learning_manager),
    current_user: User = Depends(get_current_active_user)
):
    try:
        pairs = await learning_manager.get_all_pairs(user_id=current_user.id) # Simplified
        
        drafts = []
        for pair in pairs[:limit]:
            if status is None or pair.status == status:
                drafts.append({
                    "id": pair.id,
                    "thread_id": pair.thread_id,
                    "draft_content": pair.draft_content,
                    "status": pair.status,
                    "created_at": pair.created_at.isoformat(),
                    "draft_message_id": pair.draft_message_id
                })
        
        return DraftListResponse(drafts=drafts)
    except Exception as e:
        raise ServiceUnavailableError("email", str(e))

@router.delete("/draft/{draft_id}", response_model=DeleteDraftResponse)
@limiter.limit(RATE_LIMITS["email"])
async def delete_draft(request: Request, 
    draft_id: int,
    learning_manager: LearningManager = Depends(get_learning_manager),
    current_user: User = Depends(get_current_active_user)
):
    try:
        success = await learning_manager.delete_pair(pair_id=draft_id)
        if success:
            return DeleteDraftResponse(success=True, message="Draft deleted.")
        else:
            raise DocumentNotFoundError("draft", collection="email_drafts")
    except Exception as e:
        raise ServiceUnavailableError("email", str(e))

@router.get("/inbox/folder", response_model=EmailResponse)
@limiter.limit(RATE_LIMITS["email"])
async def get_inbox_from_folder(request: Request, 
    folder_name: str,
    max_results: int = 10,
    client: AbstractEmailClient = Depends(get_email_client),
    current_user: User = Depends(get_current_active_user)
):
    try:
        emails = await client.get_emails_from_folder(
            folder_name=folder_name,
            max_results=max_results
        )
        return EmailResponse(
            emails=emails,
            count=len(emails),
            user_id=current_user.id,
            configured=True
        )
    except Exception as e:
        raise ServiceUnavailableError("email", str(e))