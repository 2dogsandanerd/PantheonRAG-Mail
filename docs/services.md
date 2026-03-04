# PantheonMail — Service-Architektur

Detaillierte Übersicht aller Services und Komponenten in PantheonMail v5.0.

---

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Email Services](#email-services)
3. [RAG Services](#rag-services)
4. [Learning Services](#learning-services)
5. [Infrastructure Services](#infrastructure-services)
6. [API Services](#api-services)
7. [Worker Services](#worker-services)
8. [Externe Integration](#externe-integration)

---

## Übersicht

### Service-Kategorien

| Kategorie | Anzahl | Beschreibung |
|-----------|--------|--------------|
| **Email Services** | 5 | IMAP/Gmail, Draft, Thread-Verwaltung |
| **RAG Services** | 6 | Ingestion, Query, Collection, Graph-Lite |
| **Learning Services** | 3 | Learning Manager, Selective Spock |
| **Infrastructure** | 5 | Config, Health Monitor, Service Manager |
| **API Layer** | 15 | FastAPI Router für alle Endpunkte |
| **Worker** | 2 | Celery Tasks, Background Jobs |

---

## Email Services

### 1. Email Client Service

**Datei:** `src/core/email_clients/`

**Verantwortlichkeit:**
- IMAP-Verbindung zu Email-Providern
- Gmail OAuth2-Authentifizierung
- SSL/TLS-Verschlüsselung
- E-Mail-Abruf und -Verarbeitung

**Klassen:**
- `AbstractEmailClient` — Basis-Klasse
- `IMAPClient` — IMAP-Implementierung
- `GmailClient` — Gmail mit OAuth2

**Methoden:**
```python
async def get_unread_emails(max_results: int = 10) -> List[Dict]
async def get_thread_history(thread_id: str) -> List[Dict]
async def create_draft(to: str, subject: str, body: str) -> str
async def clear_inbox() -> Dict
async def get_emails_from_folder(folder_name: str, max_results: int) -> List[Dict]
```

**Konfiguration:**
```bash
EMAIL_PROVIDER=imap  # oder gmail
EMAIL_USER=user@example.com
EMAIL_PASSWORD=app-password
IMAP_HOST=imap.example.com
IMAP_PORT=993
```

---

### 2. Draft Service

**Datei:** `src/services/draft_service.py`

**Verantwortlichkeit:**
- AI-generierte Antwortentwürfe
- RAG-Kontext-Integration
- Prompt-Engineering
- LLM-Aufrufe (Ollama, OpenAI, Gemini, Anthropic)

**Methoden:**
```python
async def generate_draft_with_learning(
    email_data: Dict,
    user_id: int,
    thread_id: str,
    use_rag: bool = True
) -> Dict:
    """Generiert Antwortentwurf mit optionalem RAG-Kontext"""
    
async def filter_emails_batch(
    email_list: List[Dict],
    user_id: int
) -> Dict:
    """Filtert E-Mails nach Relevanz (Auto-Filter)"""
```

**Fiat Lean Mode:**
- Priorisiert Docling für digitale Dokumente
- Multi-Lane "Refinery" nur bei niedriger Konfidenz (< 0.85)
- Optimierte Prompt-Templates für schnelle Generierung

**LLM-Provider:**
```python
# Unterstützte Provider
LLM_PROVIDER=ollama  # oder openai, gemini, anthropic
LLM_MODEL=llama3:latest
```

---

### 3. Learning Manager

**Datei:** `src/services/learning_manager.py`

**Verantwortlichkeit:**
- Speichert Draft-Sent-Paare (Learning Pairs)
- Verwaltet Feedback und Ratings
- Löst Selective Spock Chunking aus
- Matched gesendete E-Mails mit Entwürfen

**Methoden:**
```python
async def add_draft(
    user_id: int,
    thread_id: str,
    draft_message_id: str,
    draft_content: str
) -> int:
    """Speichert Draft als Learning Pair"""

async def get_all_pairs(user_id: int) -> List[LearningPair]
async def delete_pair(pair_id: int) -> bool
async def get_stats(user_id: int) -> Dict
async def match_sent_emails(
    email_client: AbstractEmailClient,
    user_id: int
) -> Dict:
    """Matcht gesendete E-Mails mit pending Drafts"""
```

**Database Model:**
```python
class LearningPair(Base):
    id: int
    user_id: int
    thread_id: str
    draft_message_id: str
    draft_content: str
    sent_message_id: str  # Nach dem Senden
    sent_content: str
    status: str  # DRAFT_CREATED, PAIR_COMPLETED
    rating: float
    created_at: datetime
```

---

### 4. Selective Spock Service

**Datei:** `src/services/generators/` (Spock-Integration)

**Verantwortlichkeit:**
- Semantisches Chunking von Learning Pairs
- Identifiziert Bedeutungsgrenzen im Text
- Erstellt kontextreiche Chunks für RAG

**Funktionsweise:**
1. Analysiert Korrekturpaar (Original → Verbessert)
2. Identifiziert semantische Blöcke
3. Erstelt Chunks mit Metadaten
4. Indiziert in "learning_kb" Collection

**Nur für Learning Pairs:**
- Allgemeine Dokumente verwenden schnelleres Character-Splitting
- Learning Pairs erhalten hochwertige semantische Chunks

---

## RAG Services

### 5. Ingestion Service

**Datei:** `src/services/ingestion_processor.py`, `src/services/docling_service.py`

**Verantwortlichkeit:**
- Dokumentenverarbeitung mit Docling
- Chunking (semantisch, rekursiv, fixed-size)
- Embedding-Generierung
- Indexierung in ChromaDB

**Unterstützte Formate:**
- PDF (digital & gescannt mit OCR)
- DOCX (Word)
- XLSX (Excel)
- TXT, Markdown
- PPTX (PowerPoint, eingeschränkt)

**Pipeline:**
```python
async def ingest_document(
    file_path: str,
    collection_name: str,
    chunk_size: int = 512,
    chunk_overlap: int = 128
) -> Dict:
    """
    1. Dokument mit Docling parsen
    2. Struktur extrahieren (Header, Tabellen, Bilder)
    3. Chunking anwenden
    4. Embeddings generieren
    5. In ChromaDB indexieren
    """
```

**Docling-Integration:**
- `pipeline_fast` für digitale PDFs
- `pipeline_ocr` für gescannte Dokumente
- Strukturerkennung (Tabellen, Listen, Header)

---

### 6. Query Service

**Datei:** `src/api/v1/rag/query.py`, `src/core/rag_client.py`

**Verantwortlichkeit:**
- Hybrid-Suche (Vektor + BM25)
- Reranking (optional)
- Context-Aggregation
- Query-Routing (domänenbasiert)

**Methoden:**
```python
async def query(
    query_text: str,
    collection_names: List[str],
    n_results: int = 5,
    use_reranker: bool = False
) -> Dict:
    """
    1. Query embedden
    2. Vektor-Ähnlichkeitssuche in ChromaDB
    3. BM25-Keyword-Suche
    4. Ergebnisse kombinieren (Hybrid)
    5. Optional: Reranking
    6. Kontext aggregieren
    """
```

**Hybrid Search:**
```python
# Vektor-Suche (semantisch)
vector_results = chroma_collection.query(
    query_embeddings=[query_embedding],
    n_results=k
)

# BM25-Suche (keyword-basiert)
bm25_results = bm25_index.search(query_text, k=k)

# Kombinieren (Reciprocal Rank Fusion)
final_results = reciprocal_rank_fusion(vector_results, bm25_results)
```

---

### 7. Collection Manager

**Datei:** `src/core/collection_manager.py`, `src/core/chroma_manager.py`

**Verantwortlichkeit:**
- CRUD-Operationen für Collections
- Metadata-Verwaltung
- Collection-Registry
- ChromaDB-Client-Management

**Methoden:**
```python
async def create_collection(
    name: str,
    embedding_config: Dict = None
) -> Collection
async def delete_collection(name: str) -> bool
async def list_collections() -> List[Collection]
async def get_collection(name: str) -> Collection
```

**ChromaManager:**
- Singleton für ChromaDB-Client
- Verbindungsmanagement (Startup/Shutdown)
- Health-Checks

---

### 8. Graph-Lite Service

**Datei:** `src/services/graph_lite_service.py`

**Verantwortlichkeit:**
- SQLite-basierte Entity-Relations (statt Neo4j)
- Fakten-Extraktion aus Dokumenten
- Injektion in RAG-Prompts

**Database Schema:**
```sql
CREATE TABLE graph_lite_facts (
    id INTEGER PRIMARY KEY,
    entity_type VARCHAR(50),
    entity_value VARCHAR(255),
    relation_type VARCHAR(50),
    related_entity_type VARCHAR(50),
    related_entity_value VARCHAR(255),
    confidence FLOAT,
    source_doc_id VARCHAR(255),
    created_at DATETIME
);
```

**Beispiel-Fakten:**
```
(Person, "Max Mustermann", "arbeitet_für", "Firma", "ACME GmbH", 0.95, "doc_123")
(Projekt, "Alpha", "hat_Budget", "Budget", "100000", 0.98, "doc_456")
```

**Nutzung im Draft:**
```python
# Bei Query "Wer leitet Projekt Alpha?"
facts = graph_lite.get_facts_for_query("Projekt Alpha")
# → Injiziere Fakt in LLM-Prompt:
# "Projekt Alpha hat ein Budget von 100.000€"
```

---

### 9. External RAG Connector

**Datei:** `src/services/external_rag_connector.py`

**Verantwortlichkeit:**
- Proxy zu externem RAG-Modul
- API-Adapter für Knowledge-Base-Kit
- Fallback bei lokaler RAG

**Konfiguration:**
```bash
EXTERNAL_RAG_ENABLED=true
EXTERNAL_RAG_URL=http://localhost:8080
EXTERNAL_RAG_TIMEOUT=60
```

**Methoden:**
```python
async def query(
    query_text: str,
    collection_names: List[str],
    n_results: int = 5
) -> Dict

async def index_documents(
    documents: List[Dict],
    collection_name: str
) -> Dict

async def list_collections() -> Dict
```

---

## Infrastructure Services

### 10. Config Service

**Datei:** `src/services/config_service.py`

**Verantwortlichkeit:**
- Hot-Reload-fähige Konfiguration
- .env-Datei lesen/schreiben
- Konfigurationsvalidierung
- Runtime-Updates ohne Neustart

**Methoden:**
```python
def load_configuration() -> Dict
def save_configuration(config: Dict) -> bool
def validate_config(config: Dict) -> List[Dict]
def get_value(key: str, default: Any = None) -> Any
```

**Hot-Reload:**
```python
# Liest frische .env bei jedem Aufruf
config = config_service.load_configuration(use_hot_reload=True)
```

---

### 11. Health Monitor

**Datei:** `src/services/health_monitor.py`

**Verantwortlichkeit:**
- Hintergrund-Überwachung aller Dienste
- WebSocket-Updates für Frontend
- Alerting bei Fehlern
- Auto-Recovery-Versuche

**Überwachte Dienste:**
- ChromaDB (HTTP Heartbeat)
- Ollama (API-Check)
- Redis (Ping)
- Database (Connection Test)
- External RAG (HTTP Health)

**Konfiguration:**
```python
class HealthMonitorConfig:
    check_interval: int = 5  # Sekunden
    event_debounce: int = 2  # Sekunden (Anti-Flapping)
    max_subscribers: int = 10  # WebSocket-Clients
```

**WebSocket-Events:**
```json
{
  "event": "service_status_change",
  "service": "chromadb",
  "status": "unhealthy",
  "timestamp": "2026-03-01T10:00:00"
}
```

---

### 12. Service Manager

**Datei:** `src/services/service_manager.py`

**Verantwortlichkeit:**
- Startet/stoppt externe Dienste (ChromaDB, Ollama)
- Health-Checks beim Startup
- Graceful Shutdown
- Prozess-Management

**Startup-Sequenz:**
```python
async def startup():
    # 1. ChromaDB starten
    chroma_result = await start_chroma(config)
    
    # 2. Ollama starten
    ollama_result = await start_ollama(config)
    
    # 3. ChromaDB-Client verbinden
    chroma_client = get_chroma_manager().get_client()
    
    # 4. Database initialisieren
    await init_db()
```

**Shutdown-Sequenz:**
```python
async def shutdown():
    # 1. Health Monitor stoppen
    await health_monitor.stop()
    
    # 2. ChromaDB-Client schließen (wichtig!)
    get_chroma_manager().close_client()
    
    # 3. Dienste stoppen
    await stop_chroma()
    await stop_ollama()
    
    # 4. Database-Engine disposen
    await engine.dispose()
```

---

### 13. Onboarding Service

**Datei:** `src/services/onboarding_service.py`

**Verantwortlichkeit:**
- Setup-Wizard Logik
- Konfigurationsvalidierung
- Fortschrittsverfolgung
- Erste Schritte führen

**Onboarding-Schritte:**
```python
steps = {
    "email_configured": False,
    "llm_configured": False,
    "first_document_uploaded": False,
    "first_draft_generated": False
}
```

**Methoden:**
```python
async def get_status(user_id: int) -> Dict
async def complete_step(user_id: int, step: str) -> bool
async def validate_email_config(config: Dict) -> Dict
```

---

### 14. Analytics Service

**Datei:** `src/services/analytics_service.py`

**Verantwortlichkeit:**
- Nutzungsstatistiken sammeln
- LLM-Token-Tracking
- API-Call-Metriken
- Dashboard-Daten

**Metriken:**
```python
{
    "total_queries": 1000,
    "total_tokens": 500000,
    "avg_response_time_ms": 2500,
    "emails_processed": 150,
    "drafts_generated": 120,
    "learning_pairs": 45
}
```

---

## API Services (FastAPI Router)

### 15. Authentication Router

**Datei:** `src/api/v1/auth.py`

**Endpunkte:**
- `POST /auth/register` — User registrieren
- `POST /auth/login` — User anmelden
- `POST /auth/refresh` — Token erneuern
- `GET /auth/me` — Current User

**JWT-Integration:**
- Access Token (30 Minuten)
- Refresh Token (7 Tage, Rotation)
- DEV_MODE (ohne Auth)

---

### 16. Email Router

**Datei:** `src/api/v1/email.py`

**Endpunkte:**
- `GET /email/inbox` — Ungelesene E-Mails
- `GET /email/thread/{thread_id}` — Thread-Historie
- `POST /email/draft` — Draft generieren
- `POST /email/draft/save` — Draft speichern
- `GET /email/drafts` — Entwürfe auflisten
- `DELETE /email/draft/{draft_id}` — Draft löschen
- `POST /email/clear-inbox` — Inbox bereinigen
- `GET /email/inbox/folder` — E-Mails aus Ordner

---

### 17. RAG Router

**Datei:** `src/api/v1/rag/`

**Endpunkte:**
- `POST /rag/query` — RAG-Abfrage
- `POST /rag/add-text` — Text hinzufügen
- `POST /rag/create-collection` — Collection erstellen
- `DELETE /rag/delete-collection` — Collection löschen
- `GET /rag/list-collections` — Collections auflisten

**Sub-Routers:**
- `documents/upload.py` — Datei-Upload
- `documents/query.py` — Dokumenten-Query
- `documents/management.py` — Dokumenten-Verwaltung
- `ingestion/` — Ingestion-Status, Analyse

---

### 18. Learning Router

**Datei:** `src/api/v1/learning.py`

**Endpunkte:**
- `POST /learning/match-sent-emails` — Sent-Matching
- `GET /learning/stats` — Learning-Statistiken
- `GET /learning/pairs` — Alle Learning Pairs
- `DELETE /learning/draft/{draft_id}` — Draft löschen

---

### 19. Dashboard Router

**Datei:** `src/api/v1/dashboard.py`

**Endpunkte:**
- `GET /dashboard/stats` — Dashboard-Statistiken
- `GET /dashboard/conversations` — Letzte Konversationen
- `GET /dashboard/email-stats` — E-Mail-Statistiken

---

### 20. Configuration Router

**Datei:** `src/api/v1/config.py`

**Endpunkte:**
- `GET /config/config` — Konfiguration abrufen
- `POST /config/config` — Konfiguration speichern
- `POST /config/config/test` — Verbindungen testen
- `GET /config/models` — Verfügbare LLM-Modelle

---

### 21. Weitere Router

| Router | Datei | Endpunkte |
|--------|-------|-----------|
| **Auto-Draft** | `auto_draft.py` | Start/Stop/Status |
| **Services** | `services.py` | Service-Status/Restart |
| **Onboarding** | `onboarding/` | Status/Complete |
| **Statistics** | `statistics.py` | Usage/LLM-Stats |
| **Cache** | `cache/` | Clear/Stats |
| **Tasks** | `tasks.py` | List/Cancel |
| **Evaluation** | `evaluation/` | Evaluate/Results |
| **Feedback** | `feedback/` | Submit/List |
| **Upgrade** | `upgrade/` | Check/Apply |

---

## Worker Services

### 22. Celery Worker

**Datei:** `src/workers/`, `src/tasks/`

**Verantwortlichkeit:**
- Asynchrone Hintergrundtasks
- Document Ingestion (große Dateien)
- Batch-Verarbeitung
- Scheduled Jobs (Auto-Draft)

**Tasks:**
```python
@celery.task
def ingest_document_task(file_path: str, collection_name: str) -> Dict

@celery.task
def generate_draft_task(email_data: Dict, user_id: int) -> str

@celery.task
def match_sent_emails_task(user_id: int) -> Dict
```

**Konfiguration:**
```bash
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

---

### 23. Auto-Draft Worker

**Datei:** `src/services/auto_draft_service.py`

**Verantwortlichkeit:**
- Hintergrund-Überwachung neuer E-Mails
- Automatische Draft-Generierung
- Konfigurierbare Intervalle

**Intervall:**
```bash
AUTO_DRAFT_INTERVAL=300  # Sekunden (5 Minuten)
```

**Endpunkte:**
- `POST /auto-draft/start` — Worker starten
- `POST /auto-draft/stop` — Worker stoppen
- `GET /auto-draft/status` — Status abrufen

---

## Service-Interaktion

### Beispiel: Draft-Generierung

```
1. User klickt "Generate Draft" im Frontend
   ↓
2. Frontend → POST /api/v1/email/draft
   ↓
3. Email Router → DraftService.generate_draft_with_learning()
   ↓
4. DraftService → RAG-Query (wenn use_rag=true)
   ↓
5. RAG-Service → Hybrid-Suche in ChromaDB
   ↓
6. RAG-Service → Graph-Lite Facts (wenn verfügbar)
   ↓
7. DraftService → LLM-Prompt erstellen
   ↓
8. DraftService → LLM-Provider (Ollama/OpenAI)
   ↓
9. LLM generiert Antwort
   ↓
10. DraftService → Antwort an Frontend
    ↓
11. User speichert Draft → POST /api/v1/email/draft/save
    ↓
12. LearningManager → LearningPair speichern
    ↓
13. Selective Spock → Semantische Chunks erstellen
    ↓
14. RAG-Service → Chunks in "learning_kb" indexieren
```

---

## Lizenz

Dieses Projekt steht unter der AGPL-3.0 Lizenz.
