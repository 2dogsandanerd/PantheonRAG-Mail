from src.core.auth import get_current_active_user
from src.database.models import User
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union, TYPE_CHECKING

from src.api.v1.dependencies import get_rag_client
from src.services.external_rag_connector import ExternalRAGConnector

if TYPE_CHECKING:
    from src.core.rag_client import RAGClient

class QueryRequest(BaseModel):
    query: str
    collection_name: str = "default"
    k: int = 5

class QueryResponse(BaseModel):
    results: List[str]
    metadata: List[Dict[str, Any]]

class AddTextRequest(BaseModel):
    text: str
    metadata: Dict[str, Any]
    collection_name: str = "default"

class AddTextResponse(BaseModel):
    success: bool
    message: str
    ids: List[str]

class CollectionRequest(BaseModel):
    collection_name: str

class CollectionResponse(BaseModel):
    success: bool
    message: str

class CollectionsResponse(BaseModel):
    collections: List[str]

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    current_user: User = Depends(get_current_active_user),
    rag_client: Union["RAGClient", ExternalRAGConnector] = Depends(get_rag_client),
):
    """Query the RAG system (Local fallback or External Proxy)."""
    try:
        if isinstance(rag_client, ExternalRAGConnector):
            # Proxy to external RAG
            response = await rag_client.query(
                query_text=request.query,
                collection_names=[request.collection_name],
                n_results=request.k
            )
            return QueryResponse(
                results=[item["content"] for item in response.get("context", [])],
                metadata=[item["metadata"] for item in response.get("context", [])]
            )
        else:
            # Local fallback
            results, metadata = await rag_client.query(
                request.query,
                collection_name=request.collection_name,
                k=request.k
            )
            return QueryResponse(results=results, metadata=metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-text", response_model=AddTextResponse)
async def add_text_to_rag(
    request: AddTextRequest,
    current_user: User = Depends(get_current_active_user),
    rag_client: Union["RAGClient", ExternalRAGConnector] = Depends(get_rag_client),
):
    """Add text to RAG (Local or External)."""
    try:
        if isinstance(rag_client, ExternalRAGConnector):
            # We map this to index_documents in the external connector
            doc = {
                "text": request.text,
                "metadata": request.metadata,
                "doc_id": f"api_{hash(request.text)}"
            }
            response = await rag_client.index_documents([doc], request.collection_name)
            if response.get("success"):
                return AddTextResponse(
                    success=True, 
                    message="Text added successfully to external RAG", 
                    ids=[]
                )
            else:
                raise Exception(response.get("error", "External error"))
        else:
            ids = await rag_client.add_text(
                request.text,
                request.metadata,
                collection_name=request.collection_name
            )
            return AddTextResponse(
                success=True, 
                message="Text added successfully", 
                ids=ids
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-collection", response_model=CollectionResponse)
async def create_collection(
    request: CollectionRequest,
    current_user: User = Depends(get_current_active_user),
    rag_client: Union["RAGClient", ExternalRAGConnector] = Depends(get_rag_client),
):
    """Create a new collection."""
    try:
        if isinstance(rag_client, ExternalRAGConnector):
            response = await rag_client.create_collection(request.collection_name)
            if response.get("success"):
                return CollectionResponse(success=True, message=f"External collection '{request.collection_name}' created.")
            else:
                raise Exception(response.get("error", "External error"))
        else:
            await rag_client.create_collection(request.collection_name)
            return CollectionResponse(success=True, message=f"Local collection '{request.collection_name}' created.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-collection", response_model=CollectionResponse)
async def delete_collection(
    request: CollectionRequest,
    current_user: User = Depends(get_current_active_user),
    rag_client: Union["RAGClient", ExternalRAGConnector] = Depends(get_rag_client),
):
    """Delete a collection."""
    try:
        # Note: External connector might not have a direct delete_collection exposed in the same way
        # but we can try if it's implemented or fallback
        if isinstance(rag_client, ExternalRAGConnector):
             # Current ExternalRAGConnector doesn't have delete_collection exposed yet?
             # Let's assume for now we might need to add it or raise error
             raise HTTPException(status_code=501, detail="Delete collection not yet supported for external RAG")
        else:
            await rag_client.delete_collection(request.collection_name)
            return CollectionResponse(success=True, message=f"Collection '{request.collection_name}' deleted.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list-collections", response_model=CollectionsResponse)
async def list_collections(
    current_user: User = Depends(get_current_active_user),
    rag_client: Union["RAGClient", ExternalRAGConnector] = Depends(get_rag_client),
):
    """List all RAG collections."""
    try:
        if isinstance(rag_client, ExternalRAGConnector):
            response = await rag_client.list_collections()
            return CollectionsResponse(collections=response.get("collections", []))
        else:
            collections = await rag_client.list_collections()
            return CollectionsResponse(collections=collections)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
