#!/usr/bin/env python3
"""
Migrations-Script: Collections von lokaler ChromaDB → externes RAG-Modul

Usage:
    python scripts/migrate_collections.py --dry-run
    python scripts/migrate_collections.py --execute
"""

import asyncio
import sys
import argparse
from pathlib import Path
from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from src.core.rag_client import RAGClient
from src.services.external_rag_connector import ExternalRAGConnector
from src.services.config_service import config_service


async def migrate_collections(dry_run=True, external_url="http://localhost:8080"):
    """
    Migriert alle Collections von lokaler ChromaDB zum externen RAG-Modul
    """
    logger.info(f"🚀 Starting collection migration (dry_run={dry_run})")
    
    # 1. Lokale RAG-Client initialisieren
    logger.info("Initializing local RAG client...")
    config = config_service.load_configuration()
    local_rag = RAGClient(config=config)
    
    # 2. Externe RAG-Verbindung
    logger.info(f"Connecting to external RAG at {external_url}...")
    external_rag = ExternalRAGConnector(base_url=external_url)
    
    # Health check
    health = await external_rag.health_check()
    if not health.get("success"):
        logger.error(f"❌ External RAG is not healthy: {health.get('error')}")
        return False
    
    logger.success(f"✅ External RAG is healthy")
    
    # 3. Lokale Collections auflisten
    logger.info("Listing local collections...")
    local_collections_response = await local_rag.list_collections()
    
    if not local_collections_response.is_success:
        logger.error(f"❌ Failed to list local collections: {local_collections_response.error}")
        return False
    
    local_collections = local_collections_response.data
    logger.info(f"Found {len(local_collections)} local collections: {local_collections}")
    
    # 4. Für jede Collection migrieren
    migrated = 0
    failed = 0
    
    for collection_name in local_collections:
        logger.info(f"\n📦 Processing collection: {collection_name}")
        
        try:
            # 4.1. Alle Dokumente holen
            logger.info(f"  Fetching documents from {collection_name}...")
            docs_response = await local_rag.get_documents(collection_name, limit=10000)
            
            if not docs_response or not docs_response.get("documents"):
                logger.warning(f"  ⚠️  No documents found in {collection_name}")
                continue
            
            documents = docs_response["documents"]
            logger.info(f"  Found {len(documents)} documents")
            
            if dry_run:
                logger.info(f"  [DRY RUN] Would migrate {len(documents)} documents to external RAG")
                logger.info(f"  [DRY RUN] Sample document: {documents[0][:100] if documents else 'N/A'}...")
                migrated += 1
                continue
            
            # 4.2. Collection extern erstellen
            logger.info(f"  Creating collection {collection_name} in external RAG...")
            create_response = await external_rag.create_collection(collection_name)
            
            if not create_response.get("success"):
                logger.warning(f"  ⚠️  Collection might already exist: {create_response.get('error')}")
            
            # 4.3. Dokumente indexieren
            logger.info(f"  Indexing {len(documents)} documents...")
            
            # Convert to format expected by external RAG
            docs_to_index = []
            for i, doc in enumerate(documents):
                docs_to_index.append({
                    "text": doc,
                    "metadata": {"source": "migration", "original_collection": collection_name},
                    "doc_id": f"{collection_name}_{i}"
                })
            
            index_response = await external_rag.index_documents(
                documents=docs_to_index,
                collection_name=collection_name
            )
            
            if index_response.get("success"):
                logger.success(f"  ✅ Successfully migrated {collection_name}")
                migrated += 1
            else:
                logger.error(f"  ❌ Failed to index documents: {index_response.get('error')}")
                failed += 1
                
        except Exception as e:
            logger.error(f"  ❌ Error migrating {collection_name}: {e}")
            failed += 1
    
    # 5. Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Migration Summary:")
    logger.info(f"  Total collections: {len(local_collections)}")
    logger.info(f"  Migrated: {migrated}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    logger.info(f"{'='*60}")
    
    # Cleanup
    await external_rag.close()
    await local_rag.shutdown()
    
    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="Migrate collections from local to external RAG")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (no actual migration)")
    parser.add_argument("--execute", action="store_true", help="Execute migration")
    parser.add_argument("--url", default="http://localhost:8080", help="External RAG URL")
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        logger.error("❌ Please specify either --dry-run or --execute")
        sys.exit(1)
    
    dry_run = args.dry_run
    
    # Run migration
    success = asyncio.run(migrate_collections(dry_run=dry_run, external_url=args.url))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
