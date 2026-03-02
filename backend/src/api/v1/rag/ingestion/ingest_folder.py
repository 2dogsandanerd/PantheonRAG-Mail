"""
Folder Ingestion Endpoint.

Triggers asynchronous ingestion of a local folder into the RAG system.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
import os

from src.api.v1.dependencies import get_rag_client
from src.core.auth import get_current_active_user
from src.database.models import User
from src.workers.tasks import ingest_documents_task
from src.core.ingest_config import ChunkConfig

logger = logging.getLogger(__name__)
router = APIRouter()

class IngestFolderRequest(BaseModel):
    folder_path: str = Field(..., description="Absolute path to the folder to ingest")
    collection_name: str = Field(..., description="Name of the target collection")
    profile: str = Field("default", description="Ingestion profile (codebase, documents, default)")
    recursive: bool = Field(True, description="Whether to scan recursively")
    allowed_extensions: Optional[List[str]] = Field(None, description="Specific extensions to include")

@router.post("/ingest-folder")
async def ingest_folder_endpoint(
    request: IngestFolderRequest,
    current_user: User = Depends(get_current_active_user),
    rag_client=Depends(get_rag_client)
):
    """
    Start an asynchronous ingestion task for a local folder.
    
    1. Scans the folder for matching files.
    2. Creates a Celery task to process them.
    3. Returns the Task ID.
    """
    logger.info(f"Received folder ingestion request: {request.folder_path} -> {request.collection_name}")

    if not os.path.exists(request.folder_path):
        raise HTTPException(status_code=404, detail=f"Folder not found: {request.folder_path}")

    # 1. Determine extensions based on profile
    extensions = request.allowed_extensions
    if not extensions:
        if request.profile == "codebase":
            extensions = [".py", ".js", ".jsx", ".ts", ".tsx", ".md", ".json", ".yml", ".yaml", ".html", ".css", ".sql"]
        elif request.profile == "documents":
            extensions = [".pdf", ".docx", ".txt", ".md"]
        else:
            # Default: broad set
            extensions = [".pdf", ".docx", ".txt", ".md", ".py", ".js"]
    
    extensions = [ext.lower() for ext in extensions]
    logger.info(f"Using extensions filter: {extensions}")

    # 2. Scan for files
    files_to_ingest = []
    for root, dirs, filenames in os.walk(request.folder_path):
        # Skip common ignore dirs
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", "venv", ".venv", "dist", "build"}]
        
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in extensions:
                full_path = os.path.join(root, filename)
                files_to_ingest.append(full_path)
        
        if not request.recursive:
            break
    
    if not files_to_ingest:
        raise HTTPException(status_code=400, detail="No matching files found in the specified folder.")

    logger.info(f"Found {len(files_to_ingest)} files to ingest.")

    # 3. Prepare Task Data
    # We map the file list to the 'assignments' structure expected by the task
    # Currently, the task expects a list of assignments, but let's check what 'assignments' usually looks like.
    # Looking at ingestion_processor.py, 'assignments' seems to be a list of dicts or objects.
    # Let's assume for now we pass a list of file paths and the processor handles it, 
    # OR we construct simple assignment dicts.
    
    # Constructing simple assignments. Ideally, we should use the Assignment model, 
    # but for simplicity and loose coupling, we pass dicts.
    assignments = [
        {"file_path": f, "status": "pending"} for f in files_to_ingest
    ]

    task_payload = {
        "assignments": assignments,
        "collection_name": request.collection_name,
        "chunk_size": 512, # Default, can be refined per profile later
        "chunk_overlap": 50,
        "use_retry_policy": True
    }

    # 4. Trigger Celery Task
    task = ingest_documents_task.delay(task_payload)
    
    return {
        "task_id": task.id,
        "status": "queued",
        "files_found": len(files_to_ingest),
        "message": f"Started ingestion of {len(files_to_ingest)} files into '{request.collection_name}'"
    }
