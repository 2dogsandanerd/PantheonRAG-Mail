import uuid
from typing import List, Dict, Optional, Any

class MockCollection:
    def __init__(self, name: str, metadata: Dict = None):
        self.name = name
        self.metadata = metadata or {}
        self.data: Dict[str, Dict] = {} # id -> {document, embedding, metadata}

    def add(self, ids: List[str], documents: Optional[List[str]] = None, embeddings: Optional[List[List[float]]] = None, metadatas: Optional[List[Dict]] = None):
        for i, doc_id in enumerate(ids):
            self.data[doc_id] = {
                "document": documents[i] if documents else None,
                "embedding": embeddings[i] if embeddings else None,
                "metadata": metadatas[i] if metadatas else None
            }

    def get(self, ids: Optional[List[str]] = None, limit: Optional[int] = None, offset: Optional[int] = None, include: Optional[List[str]] = None) -> Dict:
        if ids:
            # Filter by IDs
            result_ids = [doc_id for doc_id in ids if doc_id in self.data]
        else:
            # All IDs
            result_ids = list(self.data.keys())

        # Pagination
        if offset:
            result_ids = result_ids[offset:]
        if limit:
            result_ids = result_ids[:limit]

        # Construct result
        documents = []
        metadatas = []
        embeddings = []
        
        for doc_id in result_ids:
            item = self.data[doc_id]
            documents.append(item["document"])
            metadatas.append(item["metadata"])
            embeddings.append(item["embedding"])

        return {
            "ids": result_ids,
            "documents": documents,
            "metadatas": metadatas,
            "embeddings": embeddings
        }

    def delete(self, ids: Optional[List[str]] = None):
        if ids:
            for doc_id in ids:
                if doc_id in self.data:
                    del self.data[doc_id]

    @property
    def count(self) -> int:
        return len(self.data)

    def query(self, query_embeddings: List[List[float]], n_results: int = 10, include: Optional[List[str]] = None) -> Dict:
        # Mock query: return random documents or empty if empty
        if not self.data:
            return {"ids": [[]], "distances": [[]], "metadatas": [[]], "documents": [[]]}
        
        # Just return top n documents
        all_ids = list(self.data.keys())[:n_results]
        
        documents = []
        metadatas = []
        ids = []
        distances = []
        
        for doc_id in all_ids:
            item = self.data[doc_id]
            ids.append(doc_id)
            documents.append(item["document"])
            metadatas.append(item["metadata"])
            distances.append(0.5) # Mock distance

        return {
            "ids": [ids],
            "distances": [distances],
            "metadatas": [metadatas],
            "documents": [documents]
        }
    
    def modify(self, name: str = None, metadata: Dict = None):
        if name:
            self.name = name
        if metadata:
            self.metadata = metadata


class MockChromaClient:
    def __init__(self):
        self._collections: Dict[str, MockCollection] = {}

    def heartbeat(self) -> int:
        return 1

    def list_collections(self) -> List[MockCollection]:
        return list(self._collections.values())

    def create_collection(self, name: str, metadata: Optional[Dict] = None) -> MockCollection:
        if name in self._collections:
            # Verify uniqueness constraints if needed, but for now just return existing or error?
            # Chroma raises error if exists and get_or_create is False.
            # But assume create_collection implies uniqueness.
            # For simplicity, we create new or overwrite?
            # Creating new MockCollection to simulate fresh start if tests expect it?
            # Proper behavior is raise ValueError usually.
            pass 
        
        collection = MockCollection(name, metadata)
        self._collections[name] = collection
        return collection

    def get_collection(self, name: str) -> MockCollection:
        if name not in self._collections:
            raise ValueError(f"Collection {name} does not exist")
        return self._collections[name]

    def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None) -> MockCollection:
        if name in self._collections:
            return self._collections[name]
        return self.create_collection(name, metadata)

    def delete_collection(self, name: str):
        if name in self._collections:
            del self._collections[name]

    def reset(self):
        self._collections = {}
