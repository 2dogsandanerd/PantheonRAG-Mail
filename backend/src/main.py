"""
Main FastAPI application with centralized startup/shutdown management.

This module implements the new startup/shutdown architecture using FastAPI's
lifespan context manager. The architecture solves the problem of blocked ports
and CLOSE_WAIT connections by ensuring proper sequencing of service startup
and shutdown:

Startup Sequence:
1. Start managed services (ChromaDB and Ollama) via ServiceManager
2. Configure and connect to ChromaDB via ChromaManager
3. Initialize database

Shutdown Sequence:
1. Close ChromaDB client connection via ChromaManager (this is the key fix)
2. Stop managed services (ChromaDB and Ollama) via ServiceManager
3. Application terminates cleanly without blocked connections

For more details about each component:
- ServiceManager: manages external service processes (src/services/service_manager.py)
- ChromaManager: manages ChromaDB client connections (src/core/chroma_manager.py)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

# --- Lean Debug System ---
from src.utils.crash_detector import crash_detector, catch_crashes
from src.middleware.debug_middleware import DebugMiddleware
# Note: crash_detector sets up logging (WARNING + ERROR only)
# --- End Debug System ---

from src.api.v1 import (
    auth,
    email,
    learning,
    auto_draft,
    dashboard,
    config,
    services,
    docs,
    statistics,
    onboarding,
    upgrade,
    feedback,
    cache,
    tasks,
)
from src.api.v1 import evaluation
from src.api.v1.rag import router as rag_router
from src.database.database import init_db
from src.services.service_manager import service_manager
from src.core.chroma_manager import get_chroma_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Handles startup and shutdown of all connected services (Chroma, Ollama, Redis, etc.)
    """
    logger.info("🚀 PantheonMail API starting...")

    # === SECURITY CHECK: JWT_SECRET_KEY ===
    import os as _os
    _jwt_secret = _os.getenv("JWT_SECRET_KEY", "")
    if not _jwt_secret or _jwt_secret == "dev-secret-key-change-in-production" or _jwt_secret == "CHANGE_ME_generate_with_openssl_rand_-hex_32":
        logger.warning(
            "⚠️  SICHERHEITSWARNUNG: JWT_SECRET_KEY ist nicht gesetzt oder verwendet den unsicheren Standard-Wert!\n"
            "   Jeder kann damit beliebige Tokens erstellen und sich als jeder User ausgeben.\n"
            "   Sicheren Key generieren: openssl rand -hex 32\n"
            "   Dann in .env setzen: JWT_SECRET_KEY=<generierter-key>"
        )
    # === END SECURITY CHECK ===

    # Track which services were successfully started for potential rollback
    chroma_started = False
    ollama_started = False
    external_rag_enabled = False  # Initialize at the beginning

    try:
        # Startup sequence
        # 1. Start managed services (ChromaDB and Ollama)
        logger.info("Starting managed services...")
        config = {}  # Will be loaded from config_service
        try:
            from src.services.config_service import config_service

            config = config_service.load_configuration()
        except ImportError:
            logger.warning("config_service not available, using empty config")

        # Check external RAG configuration early
        external_rag_enabled = (
            config.get("EXTERNAL_RAG_ENABLED", "false").lower() == "true"
        )

        # Start services using service manager with health checks
        # Only start local services if external RAG is not enabled
        if not external_rag_enabled:
            chroma_result = await service_manager.start_chroma(config)
            logger.info(f"ChromaDB start result: {chroma_result}")
            if not chroma_result["success"]:
                logger.warning(
                    f"ChromaDB start failed: {chroma_result.get('message', 'Unknown error')}"
                )
            else:
                chroma_started = True

            ollama_result = await service_manager.start_ollama(config)
            logger.info(f"Ollama start result: {ollama_result}")
            if not ollama_result["success"]:
                logger.warning(
                    f"Ollama start failed: {ollama_result.get('message', 'Unknown error')}"
                )
                # Continue startup even if Ollama fails, as it's not required for basic functionality
            else:
                ollama_started = True
        else:
            logger.info("External RAG enabled, skipping local service startup")

        # 2. Configure and connect to ChromaDB via ChromaManager (only if external RAG is not enabled)
        if not external_rag_enabled:
            chroma_config = service_manager.service_configs.get("chroma")
            if chroma_config:
                chroma_manager_instance = get_chroma_manager()
                chroma_manager_instance.configure(
                    chroma_config["host"], chroma_config["port"]
                )
                logger.info(
                    f"ChromaManager configured with {chroma_config['host']}:{chroma_config['port']}"
                )

                # 3. Get client connection (this will create the connection)
                client = chroma_manager_instance.get_client()
                if client:
                    logger.success("ChromaDB client connection established")
                else:
                    logger.warning("Failed to establish ChromaDB client connection")
            else:
                logger.warning(
                    "ChromaDB configuration not available, skipping client initialization"
                )
        else:
            logger.info("External RAG enabled, skipping local ChromaDB initialization")

        logger.info("📚 API Docs: http://localhost:33800/docs")

        # Initialize database after services are up
        logger.info("Initializing database...")
        await init_db()  # Create database tables if they don't exist (async)

        # Start Health Monitor for background service monitoring
        logger.info("Starting health monitor...")
        from src.services.health_monitor import (
            initialize_health_monitor,
            get_health_monitor,
        )
        from src.core.config import get_health_monitor_config

        health_config = get_health_monitor_config()
        health_monitor = initialize_health_monitor(service_manager, health_config)
        health_monitor.start(config)
        logger.success("Health monitor started")

        # Initialize Observability (Tracing setup only - instrumentation happens at app level)
        logger.info("Initializing observability tracing...")
        try:
            from src.core.observability import setup_tracing

            # Setup OpenTelemetry tracing provider
            setup_tracing()
            logger.success("OpenTelemetry tracing initialized")
        except Exception as e:
            logger.warning(f"OpenTelemetry initialization failed: {e}")

        # Start Metrics Collector for system metrics
        logger.info("Starting metrics collector...")
        try:
            from src.core.observability.collectors import initialize_metrics_collector

            chroma_manager_instance = get_chroma_manager()
            metrics_collector = initialize_metrics_collector(
                chroma_manager=chroma_manager_instance, interval_seconds=60
            )
            metrics_collector.start()

            logger.success("Metrics collector started")
        except Exception as e:
            logger.warning(f"Metrics collector initialization failed: {e}")

        yield  # Application runs here

    except Exception as startup_error:
        logger.error(f"Startup error occurred: {startup_error}")
        # Attempt to clean up any started services before re-raising the error
        if chroma_started:
            try:
                await service_manager.stop_chroma()
                logger.info("Cleaned up ChromaDB service after startup failure")
            except Exception as e:
                logger.error(f"Error stopping ChromaDB after startup failure: {e}")
        if ollama_started:
            try:
                await service_manager.stop_ollama()
                logger.info("Cleaned up Ollama service after startup failure")
            except Exception as e:
                logger.error(f"Error stopping Ollama after startup failure: {e}")
        raise

    finally:
        # Shutdown sequence - always executes
        logger.info("👋 PantheonMail API shutting down...")

        # 1. Stop Health Monitor first
        logger.info("Stopping health monitor...")
        try:
            from src.services.health_monitor import get_health_monitor

            health_monitor = get_health_monitor()
            await health_monitor.stop()
            logger.success("Health monitor stopped")
        except RuntimeError:
            # Health monitor was never initialized
            logger.debug("Health monitor was not running")
        except Exception as e:
            logger.error(f"Error stopping health monitor: {e}")

        # 1b. Stop Metrics Collector
        logger.info("Stopping metrics collector...")
        try:
            from src.core.observability.collectors import get_metrics_collector

            metrics_collector = get_metrics_collector()
            await metrics_collector.stop()
            logger.success("Metrics collector stopped")
        except RuntimeError:
            # Metrics collector was never initialized
            logger.debug("Metrics collector was not running")
        except Exception as e:
            logger.error(f"Error stopping metrics collector: {e}")

        # 2. Close ChromaDB client connection (only if external RAG is not enabled)
        if not external_rag_enabled:
            logger.info("Closing ChromaDB client connection...")
            chroma_manager_instance = get_chroma_manager()
            chroma_manager_instance.close_client()
        else:
            logger.info("External RAG enabled, skipping local ChromaDB client closure")

        # 3. Stop managed services (only if external RAG is not enabled)
        if not external_rag_enabled:
            logger.info("Stopping managed services...")
            try:
                await service_manager.stop_chroma()
                chroma_started = False  # Mark as stopped
            except Exception as e:
                logger.error(f"Error stopping ChromaDB: {e}")

            try:
                await service_manager.stop_ollama()
                ollama_started = False  # Mark as stopped
            except Exception as e:
                logger.error(f"Error stopping Ollama: {e}")
        else:
            logger.info("External RAG enabled, skipping local service shutdown")

        # 4. Dispose database engine
        logger.info("Disposing database engine...")
        try:
            from src.database.database import engine

            await engine.dispose()
            logger.success("Database engine disposed")
        except Exception as e:
            logger.error(f"Error disposing database engine: {e}")

        logger.info("All services stopped successfully")


# Create FastAPI app with lifespan
app = FastAPI(
    title="PantheonMail API",
    version="1.0.0",
    description="AI-powered Email Assistant with RAG and Multi-Provider LLM Support",
    lifespan=lifespan,
)

# Register error handlers
from src.core.error_handler import register_error_handlers

register_error_handlers(app)

# Rate Limiting
from src.core.rate_limiter import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add Debug Middleware (tracks all requests)
app.add_middleware(DebugMiddleware)

# CORS Middleware
# In production (Electron app), allow all localhost origins
# The Electron app runs on various localhost ports depending on webpack dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (safe for desktop app)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Expose all headers to client
)

# Include routers
from src.api.v1.admin import router as admin_router

app.include_router(admin_router, prefix="/api/v1/admin")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(email.router, prefix="/api/v1/email", tags=["Email"])
app.include_router(rag_router, prefix="/api/v1/rag", tags=["RAG"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["Learning"])
app.include_router(auto_draft.router, prefix="/api/v1/auto-draft", tags=["Auto-Draft"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(config.router, prefix="/api/v1/config", tags=["Configuration"])
app.include_router(services.router, prefix="/api/v1/services", tags=["Services"])
app.include_router(docs.router, prefix="/api/v1/docs", tags=["Documentation"])
app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["Statistics"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
app.include_router(upgrade.router, prefix="/api/v1/upgrade", tags=["Upgrade"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["Feedback"])
app.include_router(cache.router, prefix="/api/v1/cache", tags=["Cache"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(evaluation.router, prefix="/api/v1/evaluation", tags=["Evaluation"])

# Prometheus metrics endpoint
from prometheus_client import make_asgi_app

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Auto-instrument FastAPI with OpenTelemetry
# This must be done after app creation but before the app starts handling requests
# and outside of the lifespan event loop to avoid "Cannot add middleware" errors
try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app)
except Exception as e:
    logger.warning(f"Failed to instrument app with OpenTelemetry: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "PantheonMail API", "version": "1.0.0", "docs": "/docs"}


@app.get("/api/health")
async def health():
    """
    Comprehensive Health Check Endpoint.

    Checks:
    - API Status
    - Disk Space
    - Ollama Availability
    - Write Permissions
    """
    from src.core.system_check import SystemHealthCheck

    # Run checks
    disk_status = SystemHealthCheck.check_disk_space()
    ollama_status = await SystemHealthCheck.check_ollama()

    # Check data directory permissions
    data_dir = "./data"  # Default data dir
    perm_status = SystemHealthCheck.check_permissions([data_dir])

    # Determine overall status
    overall_status = "healthy"
    if disk_status["status"] == "critical" or ollama_status["status"] == "critical":
        overall_status = "critical"
    elif disk_status["status"] == "warning" or ollama_status["status"] == "error":
        overall_status = "degraded"

    return {
        "status": overall_status,
        "checks": {
            "api": "ok",
            "disk": disk_status,
            "ollama": ollama_status,
            "permissions": perm_status,
        },
    }


# NOTE: This startup_event function is kept only for reference/compatibility
# The actual startup logic is now handled in the lifespan manager
# def startup_event():
#     """Run on application startup"""
#     logger.info("Initializing database...")
#     init_db() # Create database tables if they don't exist


@app.post("/api/shutdown")
async def shutdown():
    """Shutdown endpoint - maintained for compatibility with frontend shutdown sequence"""
    logger.info(
        "Shutdown requested via API - note: actual shutdown is handled by lifespan manager"
    )
    # The actual shutdown sequence (closing client connections and stopping services)
    # is handled in the lifespan manager, which is the proper FastAPI way
    # This endpoint is maintained for compatibility with the Electron frontend shutdown sequence
    return {"status": "shutdown initiated - handled by lifespan manager"}


# NOTE: This shutdown_event function is kept only for reference/compatibility
# The actual shutdown logic is now handled in the lifespan manager
# def shutdown_event():
#     """Run on application shutdown"""
#     # This is now handled in the lifespan manager
#     logger.info("Legacy shutdown event called but handled by lifespan")
