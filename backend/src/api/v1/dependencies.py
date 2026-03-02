"""
Async FastAPI dependencies for service injection.
All dependencies are now async to support the async migration.
"""

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from src.database.database import get_db
from src.database.models import User
from src.core.email_clients.imap_client import IMAPClient
from src.core.services.query_service import QueryService # Import QueryService
from src.services.draft_service import DraftService
from src.services.auto_draft_service import AutoDraftService
from src.services.learning_manager import LearningManager
from src.services.conversation_manager import ConversationManager
from src.services.statistics_service import StatisticsService
from src.services.analytics_service import AnalyticsService
from src.services.config_service import config_service
from src.services.external_rag_connector import get_rag_service
from src.core.feature_limits import FeatureLimits, Edition

# --- AUTH DEPENDENCY ---
# Für Development: Dummy-User (keine Auth erforderlich)
# Für Production: Echte JWT-Auth via src.core.auth
import os

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

if DEV_MODE:
    # Development: Dummy-User für alle Requests
    async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
        """Development mode: returns dummy user without JWT validation"""
        dummy_user = User(
            username="dev_user",
            email="dev@localhost",
            is_active=True,
            role="admin"
        )
        return dummy_user
else:
    # Production: Echte JWT-Auth
    from src.core.auth import get_current_user

async def get_email_client(
    current_user: User = Depends(get_current_user)
):
    """
    Async get Email Client (IMAP only).
    Raises HTTPException if not configured or authentication fails.
    """
    config = config_service.load_configuration()
    email_provider = config.get("EMAIL_PROVIDER", "").lower()

    if email_provider != "imap":
        logger.warning(f"Email provider is not 'imap' or not set. It is '{email_provider}'.")
        raise HTTPException(
            status_code=501, 
            detail="Email provider not configured. Please set EMAIL_PROVIDER='imap' in settings."
        )

    email_user = config.get("EMAIL_USER", "")
    if not email_user or email_user == "your@email.com":
        logger.warning("Email user not configured.")
        raise HTTPException(status_code=501, detail="Email user not configured in settings.")

    try:
        client = IMAPClient(session_state={}, config=config)
        if not await client.is_authenticated():
            logger.error("IMAP authentication failed.")
            raise HTTPException(status_code=401, detail="IMAP authentication failed. Check credentials.")
        return client
    except Exception as e:
        logger.error(f"Failed to create or authenticate IMAP client: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to email server: {e}")

# Singleton for RAG service (prevents connection leak)
_rag_service = None

async def get_rag_client():
    """Async get RAG service (could be RAGClient or ExternalRAGConnector) (singleton to prevent connection leak)"""
    global _rag_service
    if _rag_service is None:
        _rag_service = await get_rag_service()
        logger.info(f"RAG service singleton initialized: {type(_rag_service).__name__}")
    return _rag_service

async def get_learning_manager(
    db: AsyncSession = Depends(get_db),
    rag_client = Depends(get_rag_client)
) -> LearningManager:
    """Async get LearningManager"""
    return LearningManager(db, rag_client)

async def get_conversation_manager(db: AsyncSession = Depends(get_db)) -> ConversationManager:
    """Async get ConversationManager"""
    return ConversationManager(db)

async def get_statistics_service(db: AsyncSession = Depends(get_db)) -> StatisticsService:
    """Async get StatisticsService"""
    return StatisticsService(db)

async def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    """Async get AnalyticsService"""
    return AnalyticsService(db)

async def get_query_service(
    rag_client = Depends(get_rag_client)
) -> QueryService:
    """Async get QueryService from RAGClient"""
    # Handle both local RAGClient and external connector
    if hasattr(rag_client, 'query_service'):
        return rag_client.query_service
    else:
        # For external connector, we might need to create a compatible interface
        # For now, return a mock or raise an exception if needed
        raise NotImplementedError("QueryService not available for external RAG connector")

async def get_draft_service(
    rag_client = Depends(get_rag_client),
    learning_manager: LearningManager = Depends(get_learning_manager),
    conversation_manager: ConversationManager = Depends(get_conversation_manager)
) -> DraftService:
    """Async get DraftService"""
    config = config_service.load_configuration()

    # Check if auto-draft feature is available based on edition
    edition_str = config.get("EDITION", "developer").lower()
    try:
        edition = Edition(edition_str)
    except ValueError:
        edition = Edition.DEVELOPER  # Default to developer edition

    # Get query service if available (only for local RAGClient)
    query_service = None
    if hasattr(rag_client, 'query_service'):
        query_service = rag_client.query_service

    # If auto-draft is disabled for this edition, we may want to pass this info to DraftService
    # This allows the DraftService to behave differently based on edition
    return DraftService(
        rag_client=rag_client,
        query_service=query_service,
        learning_manager=learning_manager,
        conversation_manager=conversation_manager,
        config_override=config,
        edition=edition
    )

# Singleton for AutoDraftService
_auto_draft_service = None

async def get_auto_draft_service() -> AutoDraftService:
    """Async get AutoDraftService (singleton)"""
    global _auto_draft_service
    if _auto_draft_service is None:
        config = config_service.load_configuration()
        _auto_draft_service = AutoDraftService(config_override=config)
    return _auto_draft_service

# --- LLM Task Router Dependency ---
from src.services.llm_task_router import LLMTaskRouter
from src.services.data_classifier_service import get_data_classifier_service, DataClassifierService
from src.core.llm_singleton import LLMSingleton

async def get_llm_task_router(
    data_classifier_service: DataClassifierService = Depends(get_data_classifier_service)
) -> LLMTaskRouter:
    """Async get LLMTaskRouter"""
    llm_singleton = LLMSingleton()
    return LLMTaskRouter(
        llm_singleton=llm_singleton,
        data_classifier_service=data_classifier_service
    )
