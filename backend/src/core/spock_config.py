# backend/src/core/spock_config.py
from typing import ClassVar, Dict, Literal
from pydantic import BaseModel, Field

class SpockConfig(BaseModel):
    """
    Configuration for Spock Semantic Chunking.
    Vendored from RAG Core for Mail Edition.
    """
    
    MODEL_PRESETS: ClassVar[Dict[str, str]] = {
        "fast": "all-MiniLM-L6-v2",
        "balanced": "paraphrase-multilingual-mpnet-base-v2",
        "quality": "intfloat/multilingual-e5-large",
    }
    
    model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="SentenceTransformer model for semantic similarity"
    )
    model_preset: Literal["fast", "balanced", "quality", "custom"] = Field(
        default="fast",
        description="Preset selection (overrides model_name unless 'custom')"
    )
    
    use_gpu: bool = Field(
        default=False,
        description="Use CUDA GPU acceleration"
    )
    
    similarity_threshold: float = Field(
        default=0.5,
        ge=0.0, le=1.0,
        description="Split when similarity drops below this value"
    )
    max_chunk_size: int = Field(
        default=512,
        description="Maximum chunk size (tokens or chars based on size_unit)"
    )
    min_chunk_size: int = Field(
        default=100,
        description="Minimum chunk size to avoid tiny fragments"
    )
    size_unit: Literal["tokens", "chars"] = Field(
        default="tokens",
        description="Unit for chunk size limits"
    )
    
    overlap_sentences: int = Field(
        default=0,
        ge=0, le=5,
        description="Number of sentences to overlap between chunks"
    )
    
    @property
    def resolved_model(self) -> str:
        """Get the actual model name based on preset or custom setting."""
        if self.model_preset == "custom":
            return self.model_name
        return self.MODEL_PRESETS.get(self.model_preset, self.model_name)
