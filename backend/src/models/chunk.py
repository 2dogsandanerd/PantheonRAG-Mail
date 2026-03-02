# backend/src/models/chunk.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class Chunk(BaseModel):
    """A semantic chunk of text from a document or learning pair."""
    id: str = Field(..., description="Unique ID of the chunk")
    content: str = Field(..., description="The actual text content")
    document_id: str = Field(..., description="ID of the parent document or thread")
    page_number: Optional[int] = Field(None, description="Page number if applicable")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
