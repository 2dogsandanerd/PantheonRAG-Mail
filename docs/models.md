# PantheonMail — Datenbank-Models

Vollständige Übersicht der Datenbank-Schemata und Models in PantheonMail v5.0.

---

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Authentication & Users](#authentication--users)
3. [Email & Drafts](#email--drafts)
4. [Learning & Feedback](#learning--feedback)
5. [RAG & Collections](#rag--collections)
6. [Extraction Pipeline](#extraction-pipeline)
7. [Multi-Tenancy](#multi-tenancy)
8. [Backup & Audit](#backup--audit)
9. [Datenbank-Diagramm](#datenbank-diagramm)

---

## Übersicht

### Datenbank-Typen

| Datenbank | Zweck | Technologie |
|-----------|-------|-------------|
| **SQLite** | Metadaten, Users, Learning Pairs | SQLite 3.x |
| **ChromaDB** | Vektor-Embeddings, RAG | ChromaDB 0.5.23 |
| **Redis** | Cache, Message Queue | Redis 7.x |

### SQLite Tabellen

| Tabelle | Beschreibung |
|---------|--------------|
| `users` | Benutzerkonten |
| `tenants` | Mandanten (Multi-Tenancy) |
| `email_accounts` | Email-Konfiguration |
| `learning_pairs` | Draft-Sent-Paare |
| `conversations` | Konversations-Historie |
| `query_feedbacks` | Feedback auf Antworten |
| `settings` | Key-Value-Konfiguration |
| `collection_index_configs` | Collection-Konfiguration |
| `extraction_metadata` | Dokumenten-Metadaten |
| `extraction_results` | Extrahierter Inhalt |
| `duplication_audit_log` | Deduplizierungs-Log |
| `extraction_backup` | Backup-Informationen |
| `api_keys` | API-Schlüssel |
| `tenant_usage` | Nutzungs-Tracking |
| `collection_acl` | Zugriffsrechte |

---

## Authentication & Users

### User

**Tabelle:** `users`

Benutzerkonten für Authentifizierung und Autorisierung.

```python
class User(Base):
    __tablename__ = "users"

    id: int                      # PRIMARY KEY
    username: str                # UNIQUE, INDEX, NOT NULL
    email: str                   # UNIQUE, INDEX, NOT NULL
    hashed_password: str         # NOT NULL (bcrypt)
    is_active: bool              # DEFAULT True
    tenant_id: int               # FOREIGN KEY → tenants.id (nullable)
    role: UserRole               # ENUM: admin, user, readonly
    created_at: datetime
```

**Relationships:**
- `tenant` → Tenant
- `email_accounts` → EmailAccount (1:n)
- `learning_pairs` → LearningPair (1:n)
- `conversations` → Conversation (1:n)

**Enums:**
```python
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"
```

---

### Tenant (Multi-Tenancy)

**Tabelle:** `tenants`

Mandanten für Multi-User-Szenarien.

```python
class Tenant(Base):
    __tablename__ = "tenants"

    id: int                           # PRIMARY KEY, INDEX
    name: str                         # UNIQUE, INDEX, NOT NULL (slug)
    display_name: str                 # NOT NULL
    email: str                        # NOT NULL

    # Subscription
    subscription_tier: SubscriptionTier    # ENUM: free, pro, enterprise
    subscription_status: SubscriptionStatus # ENUM: active, suspended, cancelled

    # Quotas & Limits
    max_collections: int              # DEFAULT 5
    max_queries_per_day: int          # DEFAULT 1000
    max_api_keys: int                 # DEFAULT 5

    # Features (JSON)
    features: dict                    # JSON DEFAULT {}

    created_at: datetime              # SERVER DEFAULT now()
    updated_at: datetime              # ON UPDATE now()
```

**Enums:**
```python
class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
```

**Relationships:**
- `users` → User (1:n)
- `api_keys` → APIKey (1:n)
- `usage_records` → TenantUsage (1:n)
- `collection_acls` → CollectionACL (1:n)

---

### API Key

**Tabelle:** `api_keys`

API-Schlüssel für programmatischen Zugriff.

```python
class APIKey(Base):
    __tablename__ = "api_keys"

    id: int                    # PRIMARY KEY, INDEX
    tenant_id: int             # FOREIGN KEY → tenants.id, NOT NULL

    # Security
    key_hash: str              # UNIQUE, INDEX, NOT NULL (SHA-256)
    key_prefix: str            # NOT NULL (erste Zeichen für Anzeige)
    name: str                  # NOT NULL

    # Permissions
    scopes: list               # JSON DEFAULT ["read"]

    # Limits
    rate_limit: int            # DEFAULT 100 (requests/minute)

    # Status
    is_active: bool            # DEFAULT True
    last_used_at: datetime     # NULLABLE
    expires_at: datetime       # NULLABLE

    created_at: datetime       # SERVER DEFAULT now()
```

**Relationships:**
- `tenant` → Tenant

---

## Email & Drafts

### Email Account

**Tabelle:** `email_accounts`

Email-Konfiguration pro Benutzer.

```python
class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id: int                    # PRIMARY KEY
    user_id: int               # FOREIGN KEY → users.id, INDEX, NOT NULL
    account_name: str          # NOT NULL
    email_address: str         # NOT NULL
    provider: str              # DEFAULT "gmail" (gmail|imap)
    config: str                # NOT NULL (JSON-String)
    is_default: bool           # DEFAULT False
    created_at: datetime
```

**Config (JSON-String):**
```json
{
  "imap_host": "imap.example.com",
  "imap_port": 993,
  "email_user": "user@example.com",
  "email_password": "encrypted_password",
  "use_ssl": true,
  "oauth2_token": "optional_oauth_token"
}
```

**Relationships:**
- `user` → User

---

### Conversation

**Tabelle:** `conversations`

Konversations-Historie mit RAG-Kontext.

```python
class Conversation(Base):
    __tablename__ = "conversations"

    id: str                         # PRIMARY KEY (UUID)
    user_id: int                    # FOREIGN KEY → users.id, INDEX, NOT NULL

    # Email-Daten
    email_data: str                 # NOT NULL (JSON-String)

    # Generierte Antwort
    generated_response: str         # NOT NULL
    rag_context_used: str           # NULLABLE
    model_used: str                 # NULLABLE

    # Feedback
    feedback_score: int             # NULLABLE
    feedback_text: str              # NULLABLE
    quality_score: float            # NULLABLE

    # Learning-Status
    learned: bool                   # DEFAULT False
    draft_id: str                   # NULLABLE
    draft_status: str               # NULLABLE
    sent_mail_content: str          # NULLABLE
    user_action: str                # NULLABLE

    # Timestamps
    timestamp: datetime
    created_at: datetime
```

**Relationships:**
- `user` → User

---

## Learning & Feedback

### Learning Pair

**Tabelle:** `learning_pairs`

Draft-Sent-Paare für Learning-System.

```python
class LearningPair(Base):
    __tablename__ = "learning_pairs"

    id: int                         # PRIMARY KEY
    user_id: int                    # FOREIGN KEY → users.id, INDEX, NOT NULL
    thread_id: str                  # NOT NULL, INDEX
    draft_message_id: str           # NULLABLE
    draft_content: str              # NULLABLE
    sent_message_id: str            # UNIQUE, NULLABLE
    sent_content: str               # NULLABLE
    status: str                     # DEFAULT "DRAFT_CREATED"
    rating: float                   # DEFAULT 0.0
    created_at: datetime
    updated_at: datetime            # ON UPDATE now()
```

**Status-Werte:**
- `DRAFT_CREATED` — Draft wurde generiert
- `PAIR_COMPLETED` — Sent-Mail wurde zugeordnet
- `DELETED_NEGATIVE_EXAMPLE` — Als negatives Beispiel markiert

**Relationships:**
- `user` → User

---

### Query Feedback (ConversationFeedback)

**Tabelle:** `query_feedbacks`

Feedback auf generierte Antworten.

```python
class ConversationFeedback(Base):
    __tablename__ = "query_feedbacks"

    id: int                         # PRIMARY KEY
    user_id: int                    # FOREIGN KEY → users.id, INDEX, NOT NULL
    conversation_id: str            # FOREIGN KEY → conversations.id, INDEX
    query_text: str                 # NOT NULL
    response_text: str              # NULLABLE
    rating: float                   # DEFAULT 0.0
    feedback_text: str              # NULLABLE
    created_at: datetime
    updated_at: datetime            # ON UPDATE now()
```

**Relationships:**
- `user` → User
- `conversation` → Conversation

---

### Query Feedback (RAG)

**Tabelle:** `query_feedback`

Feedback für RAG-Abfragen (Qualitäts-Monitoring).

```python
class QueryFeedback(Base):
    __tablename__ = "query_feedback"

    id: int                         # PRIMARY KEY
    query_id: str                   # UNIQUE, INDEX, NOT NULL
    user_id: int                    # FOREIGN KEY → users.id, INDEX, NOT NULL

    # Query und Antwort
    query_text: str                 # NOT NULL
    response_text: str              # NOT NULL

    # User-Feedback
    helpful: bool                   # NULLABLE (Thumbs up/down)
    rating: int                     # NULLABLE (1-5 Sterne)
    comment: str                    # NULLABLE

    # Auto-Evaluation-Scores
    faithfulness: float             # NULLABLE
    answer_relevancy: float         # NULLABLE
    overall_score: float            # NULLABLE

    # Metadaten
    collection_names: list          # JSON NULLABLE
    context_count: int              # NULLABLE

    # Timestamps
    created_at: datetime            # INDEX
```

**Relationships:**
- `user` → User

---

## RAG & Collections

### Collection Index Config

**Tabelle:** `collection_index_configs`

Konfiguration für Collection-Index-Strategien.

```python
class CollectionIndexConfig(Base):
    __tablename__ = 'collection_index_configs'

    id: int                         # PRIMARY KEY
    collection_name: str            # UNIQUE, INDEX, NOT NULL

    # Index-Strategie
    index_strategy: str             # NOT NULL
                                    # 'vector', 'hybrid', 'pandas_agent', 'sql_agent'

    data_type: str                  # NOT NULL
                                    # 'unstructured_text', 'structured_table',
                                    # 'code', 'email', 'database'

    # Vector-Index-Einstellungen
    embedding_model: str            # NULLABLE
    embedding_provider: str         # NULLABLE
    embedding_dimensions: int       # NULLABLE
    chunk_size: int                 # DEFAULT 500
    chunk_overlap: int              # DEFAULT 50

    # Structured-Data-Einstellungen
    source_file_path: str           # NULLABLE
    connection_string: str          # NULLABLE
    table_schema: dict              # JSON NULLABLE

    # Query-Routing
    priority: str                   # DEFAULT 'medium' (high, medium, low)
    enabled_for_drafts: bool        # DEFAULT True, INDEX
    weight: float                   # DEFAULT 1.0

    # Metadaten
    description: str                # NULLABLE
    created_at: datetime            # TIMEZONE
    updated_at: datetime            # TIMEZONE, ON UPDATE

    # Statistiken
    last_used: datetime             # NULLABLE
    usage_count: int                # DEFAULT 0
    avg_relevance: float            # DEFAULT 0.0
```

---

### Setting

**Tabelle:** `settings`

Key-Value-Konfiguration für Runtime-Einstellungen.

```python
class Setting(Base):
    __tablename__ = "settings"

    key: str                        # PRIMARY KEY, INDEX (max 64 Zeichen)
    value: str                      # NOT NULL
```

**Beispiele:**
```
key: "llm_provider", value: "ollama"
key: "llm_model", value: "llama3:latest"
key: "default_collection", value: "default"
```

---

### Collection ACL

**Tabelle:** `collection_acl`

Zugriffsrechte für Collections (Multi-Tenancy).

```python
class CollectionACL(Base):
    __tablename__ = "collection_acl"

    id: int                         # PRIMARY KEY, INDEX
    collection_name: str            # NOT NULL
    tenant_id: int                  # FOREIGN KEY → tenants.id, NOT NULL

    # Access Control
    allowed_roles: list             # JSON DEFAULT ["admin", "user"]
    is_public: bool                 # DEFAULT False

    created_at: datetime            # TIMEZONE

    # Unique Constraint
    __table_args__ = (
        UniqueConstraint('collection_name', 'tenant_id',
                        name='uix_collection_tenant'),
    )
```

**Relationships:**
- `tenant` → Tenant

---

## Extraction Pipeline

### Extraction Metadata

**Tabelle:** `extraction_metadata`

Metadaten für verarbeitete Dokumente.

```python
class ExtractionMetadata(Base):
    __tablename__ = "extraction_metadata"

    id: int                         # PRIMARY KEY
    file_hash: str                  # INDEX, NOT NULL (SHA-256, 64 Zeichen)
    file_path: str                  # NOT NULL (max 1024)
    file_name: str                  # NULLABLE (max 255)
    file_size: int                  # NULLABLE (Bytes)
    mime_type: str                  # NULLABLE, INDEX (max 100)
    created_date: datetime          # NULLABLE
    modified_date: datetime         # NULLABLE
    language: str                   # NULLABLE, INDEX (ISO-639, z.B. "de", "en")
    ocr_confidence: float           # NULLABLE (0-1)
    structure_score: float          # NULLABLE (0-1)
    extra: dict                     # JSON NULLABLE

    # Versioning (Phase 3)
    version: int                    # DEFAULT 1
    is_active: bool                 # DEFAULT True, INDEX
    superseded_by_id: int           # FOREIGN KEY → extraction_metadata.id
    first_seen: datetime
    last_updated: datetime

    created_at: datetime
    updated_at: datetime

    # Unique Constraint
    __table_args__ = (
        UniqueConstraint('file_hash', 'version',
                        name='uq_file_hash_version'),
    )
```

**Relationships:**
- `results` → ExtractionResultDB (1:n)
- `superseded_by` → ExtractionMetadata (self-referential)

---

### Extraction Result

**Tabelle:** `extraction_results`

Extrahierter Inhalt und Qualitätsmetriken.

```python
class ExtractionResultDB(Base):
    __tablename__ = "extraction_results"

    id: int                         # PRIMARY KEY
    metadata_id: int                # FOREIGN KEY → extraction_metadata.id, INDEX

    extracted_text: str             # NULLABLE
    extraction_engine: str          # NOT NULL (z.B. "docling", "tesseract")
    text_length: int                # NOT NULL
    quality_score: float            # NULLABLE (0-1)

    error_code: str                 # NULLABLE (max 50)
    error_message: str              # NULLABLE

    created_at: datetime
```

**Relationships:**
- `extraction_metadata` → ExtractionMetadata

---

### Duplication Audit Log

**Tabelle:** `duplication_audit_log`

Log für Deduplizierungs-Ereignisse.

```python
class DuplicationAuditLog(Base):
    __tablename__ = "duplication_audit_log"

    id: int                         # PRIMARY KEY
    original_metadata_id: int       # FOREIGN KEY → extraction_metadata.id, INDEX
    duplicate_file_path: str        # NOT NULL
    duplicate_file_hash: str        # INDEX, NOT NULL
    detection_timestamp: datetime   # INDEX
    action_taken: DuplicationAuditLogAction  # ENUM, INDEX
    user_notified: bool             # DEFAULT False
    metadata_diff: dict             # JSON NULLABLE
```

**Enums:**
```python
class DuplicationAuditLogAction(str, enum.Enum):
    SKIPPED = "SKIPPED"      # Duplicate ignoriert
    REPLACED = "REPLACED"    # Original ersetzt
    VERSIONED = "VERSIONED"  # Neue Version erstellt
    NOTIFIED = "NOTIFIED"    # User benachrichtigt
```

**Relationships:**
- `original_metadata` → ExtractionMetadata

---

## Backup & Audit

### Extraction Backup

**Tabelle:** `extraction_backup`

Backup-Informationen für Extraktion-Daten.

```python
class ExtractionBackup(Base):
    __tablename__ = "extraction_backup"

    id: int                         # PRIMARY KEY
    backup_timestamp: datetime      # INDEX
    backup_type: BackupType         # ENUM: FULL, INCREMENTAL
    records_count: int              # NOT NULL
    backup_file_path: str           # NOT NULL
    checksum: str                   # NOT NULL (SHA-256)
    compression: str                # DEFAULT "gzip" (gzip, none)
    status: BackupStatus            # DEFAULT IN_PROGRESS
```

**Enums:**
```python
class BackupType(str, enum.Enum):
    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"

class BackupStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
```

---

### Tenant Usage

**Tabelle:** `tenant_usage`

Nutzungs-Tracking für Billing und Quotas.

```python
class TenantUsage(Base):
    __tablename__ = "tenant_usage"

    id: int                         # PRIMARY KEY, INDEX
    tenant_id: int                  # FOREIGN KEY → tenants.id, NOT NULL
    date: datetime                  # NOT NULL (nur Datum)

    # Metriken
    query_count: int                # DEFAULT 0
    document_count: int             # DEFAULT 0
    token_usage: int                # DEFAULT 0 (BigInteger)
    cost_usd: float                 # DEFAULT 0.0

    # Unique Constraint
    __table_args__ = (
        UniqueConstraint('tenant_id', 'date',
                        name='uix_tenant_date'),
    )
```

**Relationships:**
- `tenant` → Tenant

---

## Datenbank-Diagramm

### Entity-Relationship-Diagramm

```
┌─────────────────┐       ┌─────────────────┐
│     tenants     │       │     users       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ tenant_id (FK)  │
│ name            │   1:n │ id (PK)         │
│ display_name    │       │ username        │
│ subscription_*  │       │ email           │
│ features (JSON) │       │ hashed_password │
└────────┬────────┘       │ role            │
         │                └────────┬────────┘
         │                         │
         │ 1:n                     │ 1:n
         │                         │
    ┌────▼────────┐          ┌─────▼────────┐
    │  api_keys   │          │email_accounts│
    ├─────────────┤          ├──────────────┤
    │ id (PK)     │          │ id (PK)      │
    │ tenant_id   │          │ user_id (FK) │
    │ key_hash    │          │ provider     │
    │ scopes      │          │ config (JSON)│
    └─────────────┘          └──────────────┘

         │                         │
         │                         │
    ┌────▼────────┐          ┌─────▼────────┐
    │tenant_usage │          │learning_pairs│
    ├─────────────┤          ├──────────────┤
    │ id (PK)     │          │ id (PK)      │
    │ tenant_id   │          │ user_id (FK) │
    │ date        │          │ thread_id    │
    │ query_count │          │ draft_*      │
    │ token_usage │          │ sent_*       │
    └─────────────┘          │ status       │
                             └──────────────┘

┌─────────────────┐       ┌─────────────────┐
│  conversations  │       │query_feedbacks  │
├─────────────────┤       ├─────────────────┤
│ id (PK, UUID)   │◄──────│ conversation_id │
│ user_id (FK)    │   1:1 │ id (PK)         │
│ email_data      │       │ user_id (FK)    │
│ response        │       │ rating          │
│ feedback_*      │       └─────────────────┘
└────────┬────────┘
         │
         │ 1:n
         │
    ┌────▼─────────────────┐
    │collection_index_config│
    ├──────────────────────┤
    │ id (PK)              │
    │ collection_name      │
    │ index_strategy       │
    │ data_type            │
    │ embedding_*          │
    │ priority             │
    └──────────────────────┘

┌─────────────────┐       ┌─────────────────┐
│extraction_meta  │       │extraction_results│
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ metadata_id (FK)│
│ file_hash       │   1:n │ id (PK)         │
│ file_path       │       │ extracted_text  │
│ version         │       │ quality_score   │
│ is_active       │       │ engine          │
│ superseded_by   │       └─────────────────┘
└────────┬────────┘
         │
         │ 1:n
         │
    ┌────▼─────────────┐
    │duplication_audit │
    ├──────────────────┤
    │ id (PK)          │
    │ original_id (FK) │
    │ action_taken     │
    └──────────────────┘
```

---

## ChromaDB Collections (Vektor-Datenbank)

### Collections

```
default                 # Standard-Wissensbasis
learning_kb            # Learning Pairs (Selective Spock)
documents_kb           # Hochgeladene Dokumente
<benutzerdefiniert>    # User-definierte Collections
```

### Collection Schema

```python
# ChromaDB Collection Struktur
{
    "name": "default",
    "metadata": {
        "embedding_model": "nomic-embed-text",
        "embedding_dimensions": 768,
        "created_by": "user_1",
        "created_at": "2026-03-01T10:00:00"
    },
    "documents": [
        {
            "id": "chunk_123",
            "content": "Text des Chunks",
            "embedding": [0.1, 0.2, ...],  # 768-dimensional
            "metadata": {
                "doc_id": "doc_456",
                "chunk_id": "chunk_123",
                "page": 1,
                "source": "document.pdf",
                "created_at": "2026-03-01T10:00:00"
            }
        }
    ]
}
```

---

## Redis Keys (Cache & Queue)

### Cache Keys

```
cache:embedding:<hash>     # Embedding-Cache
cache:query:<hash>         # Query-Ergebnis-Cache
cache:user:<user_id>       # User-Session-Cache
```

### Celery Queue

```
celery                      # Haupt-Queue
celery:results             # Task-Ergebnisse
```

### Rate Limiting

```
rate_limit:<endpoint>:<user_id>  # Rate-Limit-Counter
```

---

## Lizenz

Dieses Projekt steht unter der AGPL-3.0 Lizenz.
