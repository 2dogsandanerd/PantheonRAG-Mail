# RAG API Refactoring Plan

## Problem

`src/api/v1/rag.py` ist zu groß geworden:
- **1323 Zeilen** (kritische Grenze: ~500 Zeilen)
- **25 Funktionen** (zu viele Verantwortlichkeiten)
- **12 thematische Bereiche** (mixed concerns)

---

## Lösung: Split into Domain Routers

### Neue Struktur

```
backend/src/api/v1/rag/
├── __init__.py                    (Router aggregator)
├── collections.py                 (Collection CRUD operations)
├── documents.py                   (Document upload & browsing)
├── query.py                       (Query & search operations)
├── ingestion.py                   (Docling & batch ingestion)
└── models.py                      (Pydantic models shared across routers)
```

---

## File-by-File Breakdown

### 1. `collections.py` (~250 lines)

**Verantwortung:** Collection Management

**Endpoints:**
```python
GET    /collections                    # List all collections
POST   /collections                    # Create collection
DELETE /collections/{name}             # Delete collection
GET    /collections/{name}/stats       # Get stats
POST   /collections/{name}/reset       # Reset collection
GET    /collections/{name}/embedding-info  # Embedding compatibility
POST   /validate-upload               # Validate upload compatibility
```

**Modelle:**
- Keine (nutzt Form data)

---

### 2. `documents.py` (~350 lines)

**Verantwortung:** Document Operations (upload, browse, delete)

**Endpoints:**
```python
POST   /documents/upload              # Legacy document upload
GET    /collections/{name}/documents  # Browse documents (pagination)
DELETE /documents/{id}                # Delete document
POST   /documents/analyze             # AI document analysis
```

**Modelle:**
- Keine (nutzt `UploadFile` und Form)

---

### 3. `query.py` (~200 lines)

**Verantwortung:** RAG Query Operations

**Endpoints:**
```python
POST   /query                         # Basic RAG query
POST   /query/test                    # Query tester
POST   /query/llm                     # Query with LLM answer
GET    /stats                         # Collection stats (legacy)
```

**Modelle:**
- `QueryRequest` (existing)
- `IndexRequest` (existing)

---

### 4. `ingestion.py` (~500 lines)

**Verantwortung:** Document Ingestion (Docling, Smart Uploader, Batch Processing)

**Endpoints:**
```python
# Phase 3: Docling Async Ingestion
POST   /ingest-documents              # Start async ingestion (Docling)
GET    /ingest-status/{task_id}       # Poll ingestion status

# Phase 4: Smart Uploader
POST   /scan-folder                   # Scan folder for files
POST   /analyze-files                 # Batch AI analysis
POST   /ingest-batch                  # Multi-collection batch ingestion
```

**Background Tasks:**
- `_process_ingestion_task()` (Phase 3)
- `_process_batch_ingestion_task()` (Phase 4)

**Modelle:**
- `FilePreview`
- `AnalyzeFilesRequest`
- `FileAssignment`
- `IngestBatchRequest`

---

### 5. `models.py` (~50 lines)

**Verantwortung:** Shared Pydantic Models

```python
from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    collection: str = "project_knowledge_base"
    k: int = 5

class IndexRequest(BaseModel):
    docs_path: str
    collection: str = "project_knowledge_base"

class FilePreview(BaseModel):
    path: str
    preview: str

class AnalyzeFilesRequest(BaseModel):
    files: List[FilePreview]

class FileAssignment(BaseModel):
    file: str
    collection: str

class IngestBatchRequest(BaseModel):
    file_assignments: List[FileAssignment]
    chunk_size: int = 500
    chunk_overlap: int = 50
```

---

### 6. `__init__.py` (Router Aggregator)

**Verantwortung:** Combine all routers under `/rag` prefix

```python
from fastapi import APIRouter
from . import collections, documents, query, ingestion

# Create main RAG router
router = APIRouter()

# Include sub-routers
router.include_router(collections.router, tags=["Collections"])
router.include_router(documents.router, tags=["Documents"])
router.include_router(query.router, tags=["Query"])
router.include_router(ingestion.router, tags=["Ingestion"])
```

**Usage in `main.py`:**
```python
# BEFORE
from src.api.v1 import rag
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])

# AFTER
from src.api.v1.rag import router as rag_router
app.include_router(rag_router, prefix="/api/v1/rag")
```

---

## Migration Strategy

### Phase 1: Prepare (5 min)
1. Create `backend/src/api/v1/rag/` directory
2. Create `__init__.py` with router aggregation
3. Create `models.py` with existing Pydantic models

### Phase 2: Split Collections (10 min)
1. Copy collection endpoints to `collections.py`
2. Test endpoints work
3. Remove from original `rag.py`

### Phase 3: Split Documents (10 min)
1. Copy document endpoints to `documents.py`
2. Test endpoints work
3. Remove from original `rag.py`

### Phase 4: Split Query (5 min)
1. Copy query endpoints to `query.py`
2. Test endpoints work
3. Remove from original `rag.py`

### Phase 5: Split Ingestion (15 min)
1. Copy ingestion endpoints + background tasks to `ingestion.py`
2. Test async ingestion works
3. Remove from original `rag.py`

### Phase 6: Cleanup (5 min)
1. Delete original `rag.py`
2. Update `main.py` imports
3. Update tests (if any reference `rag.router`)
4. Run all tests

**Total Time:** ~50 minutes

---

## Benefits

✅ **Maintainability:** Each file has single responsibility
✅ **Discoverability:** Easier to find endpoints by domain
✅ **Testability:** Can test routers in isolation
✅ **Scalability:** Easier to add new endpoints
✅ **Code Review:** Smaller diffs in PRs

---

## Risks

⚠️ **Import Changes:** Existing imports will break (1-line fix in `main.py`)
⚠️ **Router Prefix:** Must ensure `/api/v1/rag` prefix is preserved
⚠️ **Dependency Injection:** All routers must import `Depends(get_rag_client)`

---

## Alternative: Keep Single File with Sections

If refactoring is too risky right now, we can keep the single file but:

1. Add clear section markers
2. Keep functions alphabetically sorted within sections
3. Extract background tasks to `src/services/ingestion_background_tasks.py`
4. Move Pydantic models to top of file

**Pro:** No breaking changes
**Con:** File still too large (harder to navigate)

---

## Recommendation

**Do the refactoring now** before Phase 5 adds more code.

Phase 5 will add:
- Collection priority system (3-5 endpoints)
- Collection wizard (1-2 endpoints)
- Re-indexing (2 endpoints)
- Collection merge (1 endpoint)
- Analytics (2-3 endpoints)

**Projected size without refactoring:** ~1800 lines (unmanageable)

---

**Status:** 📝 Plan ready
**Effort:** ~1 hour
**Priority:** ⭐⭐⭐ HIGH
