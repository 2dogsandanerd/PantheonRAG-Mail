"""
External RAG Connector for communicating with external RAG module
via REST API instead of direct RAGClient instantiation
"""

import httpx
from typing import List, Dict, Optional, Any
from loguru import logger
import asyncio

class ExternalRAGConnector:
    """
    Connector service to communicate with external RAG module
    via REST API instead of direct RAGClient instantiation
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))
        
        # Set up authentication headers
        if self.api_key:
            self.client.headers.update({"Authorization": f"Bearer {self.api_key}"})
        else:
            # Some RAG systems might use API key header differently
            self.client.headers.update({"X-API-Key": self.api_key}) if self.api_key else None
    
    async def query(self, 
                   query_text: str, 
                   collection_names: Optional[List[str]] = None,
                   n_results: int = 5) -> Dict[str, Any]:
        """
        Query the external RAG module
        """
        payload = {
            "query": query_text,
            "collections": collection_names or [],
            "k": n_results
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/rag/query",
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Transform the response to match the expected RAGClient format
            # The external RAG might return data in a different structure
            # Knowledge-Base-Self-Hosting-Kit returns: {"answer", "sources", "query", "results"}
            context_items = []
            
            # Handle different response formats from the external RAG
            if "results" in result:
                # Format from Knowledge-Base-Self-Hosting-Kit
                for item in result["results"]:
                    context_item = {
                        "content": item.get("content", item.get("document", "")),
                        "source_collection": item.get("collection", item.get("collection_name", "unknown")),
                        "relevance_score": item.get("relevance_score", item.get("similarity", 0.0)),
                        "metadata": item.get("metadata", {})
                    }
                    context_items.append(context_item)
            elif "sources" in result:
                # Alternative format
                for source in result["sources"]:
                    context_item = {
                        "content": source.get("content", source.get("document", "")),
                        "source_collection": source.get("collection", source.get("collection_name", "unknown")),
                        "relevance_score": source.get("relevance_score", source.get("similarity", 0.0)),
                        "metadata": source.get("metadata", {})
                    }
                    context_items.append(context_item)
            elif "context" in result:
                # If already in the expected format
                context_items = result["context"]
            
            transformed_result = {
                "context": context_items,
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "metadata": {
                    "collections_queried": collection_names or [],
                    "success": True,
                    "error": None,
                    "final_k": n_results
                }
            }
            
            return transformed_result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during RAG query: {e.response.status_code} - {e.response.text}")
            return {
                "context": [],
                "answer": "",
                "sources": [],
                "metadata": {
                    "collections_queried": collection_names or [],
                    "success": False,
                    "error": f"HTTP {e.response.status_code}",
                    "final_k": 0
                }
            }
        except httpx.RequestError as e:
            logger.error(f"Request error during RAG query: {str(e)}")
            return {
                "context": [],
                "answer": "",
                "sources": [],
                "metadata": {
                    "collections_queried": collection_names or [],
                    "success": False,
                    "error": str(e),
                    "final_k": 0
                }
            }
    
    async def list_collections(self) -> Dict[str, Any]:
        """
        List available collections in the RAG module
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/rag/collections"
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Transform to match expected format
            collections = []
            if "collections" in result:
                # If the external API returns a collections array
                for col in result["collections"]:
                    if isinstance(col, str):
                        collections.append({"name": col, "count": 0})  # Default count
                    elif isinstance(col, dict):
                        collections.append(col)
            else:
                # If the external API returns collection objects directly
                collections = result.get("data", [])
            
            return {
                "collections": collections,
                "success": True,
                "error": None
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during list collections: {e.response.status_code} - {e.response.text}")
            return {
                "collections": [],
                "success": False,
                "error": f"HTTP {e.response.status_code}"
            }
        except httpx.RequestError as e:
            logger.error(f"Request error during list collections: {str(e)}")
            return {
                "collections": [],
                "success": False,
                "error": str(e)
            }
    
    async def create_collection(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new collection in the RAG module
        """
        payload = {
            "name": name,
            **kwargs
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/rag/collections",
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "data": result,
                "error": None
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during create collection: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "data": None,
                "error": f"HTTP {e.response.status_code}"
            }
        except httpx.RequestError as e:
            logger.error(f"Request error during create collection: {str(e)}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    async def index_documents(self, 
                             documents: List[Dict], 
                             collection_name: str) -> Dict[str, Any]:
        """
        Index documents in the external RAG module
        """
        # Convert documents to the expected format for upload
        # The Knowledge-Base-Self-Hosting-Kit expects file uploads or specific document format
        # For now, we'll use the ingestion endpoint
        
        # Prepare the documents in the expected format
        processed_docs = []
        for doc in documents:
            if isinstance(doc, dict):
                # If it's already a dictionary with text and metadata
                processed_doc = {
                    "text": doc.get("text", doc.get("content", "")),
                    "metadata": doc.get("metadata", {}),
                    "doc_id": doc.get("doc_id", doc.get("id", ""))
                }
            else:
                # If it's a different format, try to extract content
                processed_doc = {
                    "text": str(doc),
                    "metadata": {},
                    "doc_id": ""
                }
            processed_docs.append(processed_doc)
        
        payload = {
            "documents": processed_docs,
            "collection_name": collection_name
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/rag/documents/index",  # Updated endpoint
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "data": result,
                "error": None
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during index documents: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "data": None,
                "error": f"HTTP {e.response.status_code}"
            }
        except httpx.RequestError as e:
            logger.error(f"Request error during index documents: {str(e)}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of the external RAG module
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/health"
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "status": "healthy",
                "details": result,
                "success": True,
                "error": None
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during health check: {e.response.status_code} - {e.response.text}")
            return {
                "status": "unhealthy",
                "details": {},
                "success": False,
                "error": f"HTTP {e.response.status_code}"
            }
        except httpx.RequestError as e:
            logger.error(f"Request error during health check: {str(e)}")
            return {
                "status": "unreachable",
                "details": {},
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """
        Close the HTTP client
        """
        await self.client.aclose()

# Factory function to get appropriate RAG service based on configuration
async def get_rag_service(config_override: Optional[Dict[str, Any]] = None):
    """
    Factory function to return appropriate RAG service based on configuration
    """
    from src.core.config import get_config
    from src.core.rag_client import RAGClient
    
    # Load configuration
    if config_override:
        config = config_override
    else:
        # Use the existing config service
        from src.services.config_service import config_service
        config = config_service.load_configuration()
    
    # Check if external RAG is enabled
    external_rag_enabled = str(config.get("EXTERNAL_RAG_ENABLED", "false")).lower() == "true"
    
    if external_rag_enabled:
        # Use external RAG connector
        external_rag_url = config.get("EXTERNAL_RAG_URL", "http://localhost:8080")
        external_rag_api_key = config.get("EXTERNAL_RAG_API_KEY")
        external_rag_timeout = int(config.get("EXTERNAL_RAG_TIMEOUT", "30"))
        
        logger.info(f"Using external RAG service at {external_rag_url}")
        return ExternalRAGConnector(
            base_url=external_rag_url,
            api_key=external_rag_api_key,
            timeout=external_rag_timeout
        )
    else:
        # Use local RAGClient as before
        rag_config = {
            "CHROMA_HOST": config.get("CHROMA_HOST", "127.0.0.1"),
            "CHROMA_PORT": int(config.get("CHROMA_PORT", 33801)),
            "CHROMA_IN_MEMORY": str(config.get("CHROMA_IN_MEMORY", "false")).lower() == "true",
            "LLM_PROVIDER": config.get("LLM_PROVIDER", "ollama"),
            "LLM_MODEL": config.get("LLM_MODEL", "llama3:latest"),
            "EMBEDDING_PROVIDER": config.get("EMBEDDING_PROVIDER", "ollama"),
            "EMBEDDING_MODEL": config.get("EMBEDDING_MODEL", "nomic-embed-text"),
            "EDITION": str(config.get("EDITION", "developer")).lower()
        }
        
        logger.info("Using local RAG service")
        return RAGClient(config=rag_config)