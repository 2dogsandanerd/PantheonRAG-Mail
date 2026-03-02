# backend/src/core/spock.py
"""
Spock - Semantic Logician (Fiat Edition)
Intelligent chunking based on semantic coherence.
"""
from typing import List, Optional
import numpy as np
import re
from loguru import logger

from src.core.spock_config import SpockConfig
from src.models.chunk import Chunk

class Spock:
    """Semantic Logician - Intelligent chunking based on semantic coherence."""
    
    def __init__(self, config: Optional[SpockConfig] = None):
        self.config = config or SpockConfig()
        self._model = None  # Lazy loading
    
    @property
    def model(self):
        """Lazy-load the SentenceTransformer model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            device = "cuda" if self.config.use_gpu else "cpu"
            logger.info(f"🖖 Spock (Fiat): Loading {self.config.resolved_model} on {device}")
            self._model = SentenceTransformer(self.config.resolved_model, device=device)
        return self._model
    
    def chunk_text(
        self, 
        text: str,
        document_id: str,
        metadata: Optional[dict] = None
    ) -> List[Chunk]:
        """
        Convert text into semantically coherent chunks.
        """
        if not text.strip():
            return []
        
        # 1. Split into sentences
        sentences = self._split_sentences(text)
        
        if len(sentences) == 0:
            return []
        
        if len(sentences) == 1:
            return [self._create_chunk_obj(text, 0, document_id, metadata)]
        
        # 2. Compute embeddings
        logger.debug(f"🖖 Spock: Encoding {len(sentences)} sentences...")
        embeddings = self.model.encode(sentences, show_progress_bar=False)
        
        # 3. Find boundaries
        boundaries = self._find_boundaries(embeddings)
        
        # 4. Create chunks
        chunks = []
        for i, start_idx in enumerate(boundaries):
            end_idx = boundaries[i + 1] if i + 1 < len(boundaries) else len(sentences)
            content = " ".join(sentences[start_idx:end_idx])
            
            # Simple size handling (tokens ≈ words * 1.3)
            # In Fiat edition, we prioritize speed over perfect token counting
            chunks.append(self._create_chunk_obj(content, i, document_id, metadata))
            
        logger.info(f"🖖 Spock: Created {len(chunks)} semantic chunks for {document_id}")
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        # Split on sentence-ending punctuation followed by whitespace
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _find_boundaries(self, embeddings: np.ndarray) -> List[int]:
        boundaries = [0]
        for i in range(1, len(embeddings)):
            similarity = self._cosine_similarity(embeddings[i-1], embeddings[i])
            if similarity < self.config.similarity_threshold:
                boundaries.append(i)
        return boundaries
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def _create_chunk_obj(self, content: str, idx: int, doc_id: str, meta: Optional[dict]):
        base_meta = {
            "chunk_index": idx,
            "chunking_method": "semantic",
            "model_used": self.config.resolved_model,
        }
        if meta:
            base_meta.update(meta)
            
        return Chunk(
            id=f"{doc_id}_s{idx}",
            document_id=doc_id,
            content=content,
            metadata=base_meta
        )
