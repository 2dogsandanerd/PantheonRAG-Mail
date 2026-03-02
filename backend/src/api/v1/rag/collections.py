"""
RAG Collection Management endpoints.

Handles CRUD operations for ChromaDB collections.
"""

from fastapi import APIRouter, Depends, HTTPException, Form, status, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import logging
import asyncio

from src.api.v1.dependencies import get_rag_client
from src.core.auth import get_current_active_user
from src.database.models import User, CollectionIndexConfig
from src.database.database import get_db
from src.core.collection_registry import get_collection_registry, CollectionRegistry
from src.core.exceptions import (
    CollectionNotFoundError,
    ChromaDBError,
    ValidationError
)
from src.core.feature_limits import FeatureLimits, Edition
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/collections")
async def get_collections(
    rag_client=Depends(get_rag_client),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of all ChromaDB collections."""
    logger.debug("Fetching all collections")

    response = await rag_client.list_collections()
    if not response.is_success:
        logger.error(f"Failed to list collections: {response.error}")
        raise ChromaDBError(response.error)

    collection_list = []
    for col_name in response.data:
        collection = await asyncio.to_thread(rag_client.chroma_manager.get_collection, col_name)
        count = await asyncio.to_thread(collection.count) if collection else 0
        collection_list.append({
            "name": col_name,
            "count": count
        })

    logger.info(f"Retrieved {len(collection_list)} collections")

    return {
        "collections": collection_list
    }


@router.post("/collections", status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_name: str = Form(...),
    embedding_provider: str = Form(None),
    embedding_model: str = Form(None),
    rag_client=Depends(get_rag_client),
    current_user: User = Depends(get_current_active_user)
):
    """Create new ChromaDB collection."""
    logger.debug(f"Creating collection: {collection_name} with {embedding_provider}/{embedding_model}")

    # Check if user is on Developer Edition and has reached collection limit
    if rag_client.edition == Edition.DEVELOPER:
        all_collections_response = await rag_client.list_collections()
        if all_collections_response.is_success and all_collections_response.data:
            current_count = len(all_collections_response.data)
            if current_count >= FeatureLimits.get_limit_value('max_collections', rag_client.edition):
                raise HTTPException(
                    status_code=403,
                    detail=(
                        f"Collection limit reached for Developer Edition. "
                        f"Maximum {FeatureLimits.get_limit_value('max_collections', rag_client.edition)} collection(s) allowed. "
                        "Upgrade to Team Edition for more collections."
                    )
                )

    embedding_config = {
        "provider": embedding_provider,
        "model": embedding_model
    } if embedding_provider and embedding_model else None

    response = await rag_client.create_collection(
        name=collection_name,
        embedding_config=embedding_config
    )

    if not response.is_success:
        logger.error(f"Failed to create collection '{collection_name}': {response.error}")
        raise ChromaDBError(response.error)

    logger.info(f"Collection '{collection_name}' created successfully")
    return JSONResponse(
        status_code=201,
        content={
            "success": True,
            "message": response.message,
            "collection": response.data
        }
    )


@router.delete("/collections/{collection_name}")
async def delete_collection(
    collection_name: str,
    rag_client=Depends(get_rag_client),
    current_user: User = Depends(get_current_active_user)
):
    """Delete ChromaDB collection."""
    logger.debug(f"Deleting collection: {collection_name}")

    response = await rag_client.delete_collection(collection_name)
    if not response.is_success:
        logger.error(f"Failed to delete collection '{collection_name}': {response.error}")
        raise ChromaDBError(response.error)

    logger.info(f"Collection '{collection_name}' deleted successfully")
    return {
        "success": True,
        "message": response.message
    }


@router.get("/collections/{collection_name}/stats")
async def get_collection_stats(
    collection_name: str,
    rag_client=Depends(get_rag_client),
    current_user: User = Depends(get_current_active_user)
):
    """Get statistics for a specific collection."""
    logger.debug(f"Getting stats for collection: {collection_name}")

    try:
        response = await rag_client.collection_manager.get_collection_stats(collection_name)
        if not response.is_success:
            logger.error(f"Failed to get stats for '{collection_name}': {response.error}")
            raise HTTPException(status_code=500, detail=response.error)

        logger.debug(f"Stats for '{collection_name}': {response.data}")
        return response.data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stats for '{collection_name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{collection_name}/documents")
async def get_documents(
    collection_name: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    rag_client=Depends(get_rag_client),
    current_user: User = Depends(get_current_active_user)
):
    """Get documents from a collection with pagination."""
    logger.debug(f"Fetching documents for {collection_name} with offset {offset} and limit {limit}")

    try:
        # get_documents already returns total count
        result = await rag_client.get_documents(
            collection_name=collection_name,
            offset=offset,
            limit=limit
        )

        # Extract documents and total from result
        documents = result.get("documents", [])
        total = result.get("total", 0)

        return {
            "documents": documents,
            "offset": offset,
            "limit": limit,
            "total": total,
            "has_more": (offset + len(documents)) < total
        }
    except Exception as e:
        logger.error(f"Failed to get documents for '{collection_name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collections/{collection_name}/reset")
async def reset_collection(
    collection_name: str,
    rag_client=Depends(get_rag_client),
    current_user: User = Depends(get_current_active_user)
):
    """Remove all documents from collection (keep collection)."""
    logger.debug(f"Resetting collection: {collection_name}")

    try:
        response = await rag_client.collection_manager.reset_collection(collection_name)
        if not response.is_success:
            logger.error(f"Failed to reset collection '{collection_name}': {response.error}")
            raise HTTPException(status_code=500, detail=response.error)

        logger.info(f"Collection '{collection_name}' reset successfully")
        return {
            "success": True,
            "message": response.message
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Collection reset error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Collection Registry Endpoints (Phase 1)
# ============================================

class CollectionConfigUpdate(BaseModel):
    """Schema für Collection Config Updates"""
    priority: str = "medium"  # high, medium, low
    enabled_for_drafts: bool = True
    weight: float = 1.0
    description: str = None


@router.get("/collections/configs")
async def get_all_collection_configs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Gibt alle Collection-Konfigurationen zurück"""
    logger.debug("Fetching all collection configs")

    try:
        registry = get_collection_registry(db)
        configs = await registry.get_all_configs()

        return {
            "configs": [c.to_dict() for c in configs],
            "total": len(configs)
        }
    except Exception as e:
        logger.error(f"Failed to get collection configs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{collection_name}/config")
async def get_collection_config(
    collection_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Holt Config für eine Collection"""
    logger.debug(f"Fetching config for collection: {collection_name}")

    registry = get_collection_registry(db)
    config = await registry.get_config(collection_name)

    if not config:
        raise CollectionNotFoundError(collection_name)

    return config.to_dict()


@router.put("/collections/{collection_name}/config")
async def update_collection_config(
    collection_name: str,
    update: CollectionConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Updated Collection-Config (Priority, Enabled, etc.)"""
    logger.debug(f"Updating config for collection: {collection_name}")

    registry = get_collection_registry(db)
    config = await registry.get_config(collection_name)

    if not config:
        raise CollectionNotFoundError(collection_name)

    # Update fields
    if update.priority:
        config.priority = update.priority
    if update.weight is not None:
        config.weight = update.weight
    if update.enabled_for_drafts is not None:
        config.enabled_for_drafts = update.enabled_for_drafts
    if update.description:
        config.description = update.description

    await db.commit()
    await db.refresh(config)

    logger.info(f"Updated config for '{collection_name}'")
    return {
        "message": f"Updated config for {collection_name}",
        "config": config.to_dict()
    }


@router.get("/collections/analytics")
async def get_collection_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Gibt Nutzungs-Statistiken aller Collections zurück"""
    logger.debug("Fetching collection analytics")

    try:
        registry = get_collection_registry(db)
        configs = await registry.get_all_configs()

        analytics = []
        for config in configs:
            analytics.append({
                "collection_name": config.collection_name,
                "usage_count": config.usage_count,
                "avg_relevance": config.avg_relevance,
                "last_used": config.last_used.isoformat() if config.last_used else None,
                "priority": config.priority,
                "enabled": config.enabled_for_drafts
            })

        # Sortiere nach usage_count
        analytics.sort(key=lambda x: x['usage_count'], reverse=True)

        return {
            "analytics": analytics,
            "total_collections": len(analytics)
        }
    except Exception as e:
        logger.error(f"Failed to get collection analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
