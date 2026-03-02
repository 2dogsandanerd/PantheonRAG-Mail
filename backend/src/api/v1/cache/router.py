"""
Cache Management API.

Provides endpoints for cache statistics, invalidation, and management.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from src.core.caching import get_query_cache, get_embedding_cache
from src.core.auth import get_current_active_user
from src.database.models import User, UserRole

router = APIRouter(prefix="/cache", tags=["cache"])


class CacheStats(BaseModel):
    """Cache statistics response."""
    query_cache: Dict[str, Any]
    embedding_cache: Dict[str, Any]


@router.get("/stats", response_model=CacheStats)
async def get_cache_stats(
    user: User = Depends(get_current_active_user)
):
    """
    Get cache statistics.
    
    Returns hit rates, cached items count, and other metrics.
    """
    query_cache = await get_query_cache()
    embedding_cache = await get_embedding_cache()
    
    return CacheStats(
        query_cache=await query_cache.stats(),
        embedding_cache=await embedding_cache.stats()
    )


@router.post("/clear")
async def clear_cache(
    user: User = Depends(get_current_active_user)
):
    """
    Clear all caches (admin only).
    
    ⚠️ Nur für Administratoren — leert alle Query- und Embedding-Caches.
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Nur Administratoren dürfen den Cache leeren."
        )
    
    query_cache = await get_query_cache()
    embedding_cache = await get_embedding_cache()
    
    await query_cache.clear_all()
    
    return {"message": "Cache erfolgreich geleert", "cleared_by": user.username}


@router.post("/invalidate/collection/{collection_name}")
async def invalidate_collection(
    collection_name: str,
    user: User = Depends(get_current_active_user)
):
    """
    Invalidate all cached queries for a specific collection.
    
    Use this when collection data has been updated.
    """
    query_cache = await get_query_cache()
    await query_cache.invalidate_collection(collection_name)
    
    return {"message": f"Cache invalidated for collection: {collection_name}"}
