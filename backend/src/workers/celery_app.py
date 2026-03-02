import os
from celery import Celery
from loguru import logger

# Get Redis configuration from environment variables
# Default to localhost for local development, but in Docker it will be 'redis'
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

# Construct Redis URL
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

logger.info(f"Initializing Celery with broker: {REDIS_URL}")

celery_app = Celery("pantheonmail", broker=REDIS_URL, backend=REDIS_URL)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Berlin",
    enable_utc=True,
    task_routes={
        "src.workers.tasks.ingest_documents_task": {"queue": "ingestion"},
    },
    # Dead Letter Queue Configuration (via task_reject_on_worker_lost)
    task_reject_on_worker_lost=True,
    task_acks_late=True,  # Only ack after success
)

if __name__ == "__main__":
    celery_app.start()
