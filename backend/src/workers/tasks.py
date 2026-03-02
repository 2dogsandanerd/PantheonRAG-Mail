import asyncio
from typing import Dict, Any
from loguru import logger
from celery import Task

from src.workers.celery_app import celery_app
from src.services.config_service import config_service
from src.services.external_rag_connector import get_rag_service
from src.services.ingestion_processor import create_ingestion_processor

from src.core.retry_policy import INGESTION_RETRY

@celery_app.task(
    bind=True, 
    name="src.workers.tasks.ingest_documents_task",
    autoretry_for=(Exception,), # We catch specific exceptions inside, but this is a safety net
    retry_kwargs={'max_retries': INGESTION_RETRY.max_retries},
    retry_backoff=True # Enable exponential backoff
)
def ingest_documents_task(self: Task, task_data: Dict[str, Any]):
    """
    Celery task for asynchronous document ingestion.
    
    Args:
        task_data: Dictionary containing:
            - assignments: List of file assignments
            - collection_name: Target collection
            - chunk_size: Chunk size
            - chunk_overlap: Chunk overlap
            - use_retry_policy: Boolean
    """
    logger.info(f"Starting ingestion task {self.request.id}")
    
    # 1. Load Configuration
    try:
        config = config_service.load_configuration()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {'success': False, 'error': 'Configuration load failed'}

    # 2. Initialize RAG Client
    # Use factory function to support external RAG
    try:
        # We need an async-friendly way to get the rag service in the celery task 
        # (which runs its own loop for the processor anyway)
        # Using the utility function since the loop is started in step 4
        from src.services.external_rag_connector import get_rag_service
        # Need to run factory as it is async
        rag_client = asyncio.run(get_rag_service(config_override=config))
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}")
        return {'success': False, 'error': f'RAG Service init failed: {str(e)}'}

    # 3. Define Progress Callback
    def update_progress(status: Dict[str, Any]):
        """
        Callback to update Celery task state.
        status dict contains: progress (int), processed, total, current_file
        """
        self.update_state(
            state='PROCESSING',
            meta={
                'progress': status.get('progress', 0),
                'processed': status.get('processed', 0),
                'total': status.get('total', 0),
                'current_file': status.get('current_file', ''),
                'status': 'Processing files...'
            }
        )

    # 4. Run Processor
    try:
        processor = create_ingestion_processor()
        
        # Run async processor in sync Celery task
        result = asyncio.run(processor.process(
            assignments=task_data.get('assignments', []),
            collection_name=task_data.get('collection_name', 'default'),
            rag_client=rag_client,
            progress_callback=update_progress,
            chunk_size=task_data.get('chunk_size', 500),
            chunk_overlap=task_data.get('chunk_overlap', 50),
            use_retry_policy=task_data.get('use_retry_policy', True)
        ))
        
        return result

    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        return {'success': False, 'error': str(e)}
