from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .models import Base
import os
from loguru import logger
from typing import Optional
from sqlalchemy.pool import QueuePool

# Global variables for engine and sessionmaker, to be set by init_db
engine = None
AsyncSessionLocal = None

async def init_db(database_url: Optional[str] = None):
    """
    Initialize database (async) - create tables and set up engine/sessionmaker.
    If database_url is provided, it overrides the configured URL.
    """
    global engine, AsyncSessionLocal

    if database_url:
        current_database_url = database_url
        logger.info(f"Using provided database_url for init_db: {current_database_url}")
    else:
        # Resolve database URL with UI-config support and safe default
        resolved_database_url = None
        logger.debug(f"Initial DATABASE_URL (in init_db): {resolved_database_url}")

        # 1) Try UI config service (.env hot-reload)
        try:
            from src.services.config_service import config_service
            cfg = config_service.load_configuration()
            resolved_database_url = cfg.get("lea_database_url") or cfg.get("DATABASE_URL")
            logger.debug(f"DATABASE_URL after config service (in init_db): {resolved_database_url}")
        except Exception as e:
            logger.warning(f"Config service not available for DB URL (in init_db): {e}")

        # 2) Fallback to process environment
        if not resolved_database_url:
            resolved_database_url = os.getenv("lea_database_url") or os.getenv("DATABASE_URL")
            logger.debug(f"DATABASE_URL after environment variables (in init_db): {resolved_database_url}")

        # 3) Final safety: default to local SQLite to allow first start; warn loudly
        if not resolved_database_url:
            resolved_database_url = "sqlite:///./data/learning.db"
            logger.warning("lea_database_url not set. Falling back to sqlite:///./data/learning.db. Please set lea_database_url in Settings or backend/.env.")
            logger.debug(f"DATABASE_URL after default (in init_db): {resolved_database_url}")
        
        current_database_url = resolved_database_url

    # Convert sync URL to async URL
    if current_database_url.startswith("sqlite:///"):
        ASYNC_DATABASE_URL = current_database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    elif current_database_url.startswith("postgresql://"):
        ASYNC_DATABASE_URL = current_database_url.replace("postgresql://", "postgresql+asyncpg://")
    else:
        ASYNC_DATABASE_URL = current_database_url

    logger.info(f"Final ASYNC_DATABASE_URL for engine: {ASYNC_DATABASE_URL}")

    # Create async engine with connection pooling
    # Note: SQLite doesn't support pool parameters, only use them for PostgreSQL
    if ASYNC_DATABASE_URL.startswith("sqlite"):
        engine = create_async_engine(
            ASYNC_DATABASE_URL,
            echo=False
        )
    else:
        engine = create_async_engine(
            ASYNC_DATABASE_URL,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True
        )

    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    try:
        logger.info("Creating database tables (async)...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.success("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

async def get_db():
    """
    Async dependency for database session.
    """
    if AsyncSessionLocal is None:
        await init_db() # Ensure DB is initialized if not already

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()
