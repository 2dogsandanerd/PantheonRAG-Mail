from src.core.auth import get_current_active_user
from src.database.models import User
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from collections import defaultdict

from src.api.v1.dependencies import (
    get_conversation_manager,
    get_learning_manager,
    get_statistics_service
)
from src.services.conversation_manager import ConversationManager
from src.services.learning_manager import LearningManager
from src.services.statistics_service import StatisticsService

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    conv_manager: ConversationManager = Depends(get_conversation_manager),
    learning_manager: LearningManager = Depends(get_learning_manager),
    stats_service: StatisticsService = Depends(get_statistics_service),
):
    """Async get comprehensive dashboard statistics"""
    learning_stats = await learning_manager.get_stats(current_user.id)
    # Note: ConversationManager and StatisticsService might need get_stats methods too
    # conv_stats = await conv_manager.get_stats(current_user.id)
    # dashboard_stats = await stats_service.get_dashboard_stats(current_user.id)

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username
        },
        "learning": learning_stats,
        # "conversations": conv_stats,
        # "dashboard": dashboard_stats
    }


@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_active_user),
    limit: int = 10,
    conv_manager: ConversationManager = Depends(get_conversation_manager),
):
    """Async get recent conversations for current user"""
    conversations = await conv_manager.get_user_conversations(current_user.id, limit)

    conversations_data = [
        {
            "id": c.id,
            "timestamp": c.created_at.isoformat() if c.created_at else None,
            "model_used": c.model_used,
            "feedback_score": c.feedback_score
        }
        for c in conversations
    ]

    return {
        "conversations": conversations_data,
        "count": len(conversations_data)
    }


@router.get("/email-stats")
async def get_email_statistics(
    current_user: User = Depends(get_current_active_user),
    days: int = 30,
    stats_service: StatisticsService = Depends(get_statistics_service),
):
    """Async get email statistics for the last N days"""
    daily_counts = await stats_service.get_daily_email_counts(user_id=current_user.id, days=days)
    
    return {
        "daily_counts": daily_counts,
        "total_days": days
    }