# PantheonMail — API-Referenz

> **Hinweis:** Dies ist die **Open-Source Edition (Fiat Lean Mode)**. Für Enterprise-APIs siehe [PantheonRAG Enterprise Core v4.0](../planung/manifest_v4.0.md).

**Version:** v5.0.0  
**Basis-URL:** `http://localhost:33800`  
**API-Dokumentation:** http://localhost:33800/docs  
**API-Prefix:** `/api/v1`

---

## Inhaltsverzeichnis

1. [Allgemeine Informationen](#allgemeine-informationen)
2. [Authentication API](#authentication-api)
3. [Email API](#email-api)
4. [RAG API](#rag-api)
5. [Learning API](#learning-api)
6. [Dashboard API](#dashboard-api)
7. [Configuration API](#configuration-api)
8. [Services API](#services-api)
9. [Onboarding API](#onboarding-api)
10. [Statistics API](#statistics-api)
11. [Cache API](#cache-api)
12. [Tasks API](#tasks-api)
13. [Evaluation API](#evaluation-api)
14. [Fehlerbehandlung](#fehlerbehandlung)

---

## Allgemeine Informationen

### Authentifizierung

Alle Endpunkte (außer `/auth/login`, `/auth/register` und bei `DEV_MODE=true`) erfordern einen JWT-Access-Token im Header:

```http
Authorization: Bearer <access_token>
```

### Rate Limiting

Die API verwendet Rate Limiting via SlowAPI:

| Endpunkt | Limit |
|----------|-------|
| Default | 100/Minute |
| Auth | 10/Minute (Login), 5/Minute (Register) |
| Email | 30/Minute |
| RAG | 50/Minute |
| Upload | 10/Minute |

### Antwortformat

**Erfolg (200/201):**
```json
{
  "data": {...},
  "message": "Optional message"
}
```

**Fehler:**
```json
{
  "detail": "Fehlermeldung"
}
```

---

## Authentication API

### POST `/api/v1/auth/register`

Neuen Benutzer registrieren.

**Request:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "newuser",
  "email": "user@example.com",
  "is_active": true
}
```

**Rate Limit:** 5/Minute

---

### POST `/api/v1/auth/login`

Benutzer anmelden.

**Request (Form Data):**
```
username=admin
password=secure_password
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Rate Limit:** 30/Minute

**DEV_MODE:** Bei `DEV_MODE=true` wird kein Login benötigt. Alle Endpunkte sind ohne Token zugänglich.

---

### POST `/api/v1/auth/refresh`

Access Token erneuern.

**Request:**
```
GET /api/v1/auth/refresh?refresh_token=eyJhbGci...
```

**Response (200):**
```json
{
  "access_token": "eyJhbGci...",  // Neuer Access Token
  "refresh_token": "eyJhbGci...",  // Neuer Refresh Token (Rotation)
  "token_type": "bearer"
}
```

---

### GET `/api/v1/auth/me`

Aktuellen Benutzer abrufen (geschützt).

**Request:**
```
GET /api/v1/auth/me
Authorization: Bearer eyJhbGci...
```

**Response (200):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_active": true
}
```

---

## Email API

### GET `/api/v1/email/inbox`

Ungelesene E-Mails abrufen.

**Parameter:**
- `max_results` (int, default: 10) — Maximale Anzahl
- `filter_mode` (string, default: "none") — Filtermodus ("none", "auto")

**Response (200):**
```json
{
  "emails": [
    {
      "id": "msg_123",
      "subject": "Betreff",
      "from": "sender@example.com",
      "date": "2026-03-01T10:00:00",
      "preview": "Nachrichtenvorschau..."
    }
  ],
  "count": 5,
  "user_id": 1,
  "configured": true
}
```

**Rate Limit:** 30/Minute

---

### GET `/api/v1/email/thread/{thread_id}`

Thread-Historie abrufen.

**Parameter:**
- `thread_id` (path) — Thread-ID

**Response (200):**
```json
{
  "thread": [
    {
      "id": "msg_123",
      "subject": "Re: Betreff",
      "from": "user@example.com",
      "body": "Nachrichtentext",
      "date": "2026-03-01T10:00:00"
    }
  ],
  "thread_id": "thread_123"
}
```

---

### POST `/api/v1/email/draft`

Antwortentwurf generieren (mit RAG).

**Request:**
```json
{
  "sender": "sender@example.com",
  "subject": "Betreff",
  "body": "E-Mail-Text",
  "thread_id": "thread_123",
  "use_rag": true
}
```

**Response (200):**
```json
{
  "draft": "Generierte Antwort",
  "no_answer_needed": false,
  "rag_context": "RAG-Kontext",
  "rag_status": "success",
  "rag_collection_count": 2,
  "rag_result_count": 5,
  "model": "llama3:latest"
}
```

**Rate Limit:** 30/Minute

---

### POST `/api/v1/email/draft/save`

Entwurf speichern.

**Request:**
```json
{
  "to": "empfaenger@example.com",
  "subject": "Betreff",
  "body": "Antworttext",
  "thread_id": "thread_123",
  "in_reply_to": "message_123"
}
```

**Response (200):**
```json
{
  "draft_id": "draft_123",
  "status": "created",
  "provider": "IMAPClient",
  "learning_pair_id": 456
}
```

---

### GET `/api/v1/email/drafts`

Gespeicherte Entwürfe auflisten.

**Parameter:**
- `status` (string, optional) — Filter nach Status
- `limit` (int, default: 50) — Maximale Anzahl

**Response (200):**
```json
{
  "drafts": [
    {
      "id": 1,
      "thread_id": "thread_123",
      "draft_content": "Inhalt",
      "status": "DRAFT_CREATED",
      "created_at": "2026-03-01T10:00:00"
    }
  ]
}
```

---

### DELETE `/api/v1/email/draft/{draft_id}`

Entwurf löschen.

**Parameter:**
- `draft_id` (path) — ID des zu löschenden Entwurfs

**Response (200):**
```json
{
  "success": true,
  "message": "Draft deleted."
}
```

---

### POST `/api/v1/email/clear-inbox`

Inbox bereinigen (E-Mails archivieren/löschen).

**Response (200):**
```json
{
  "success": true,
  "count": 10,
  "message": "Inbox cleared."
}
```

---

### GET `/api/v1/email/inbox/folder`

E-Mails aus spezifischem Ordner abrufen.

**Parameter:**
- `folder_name` (query) — Ordnername (z.B. "INBOX", "Sent")
- `max_results` (int, default: 10)

**Response (200):**
```json
{
  "emails": [...],
  "count": 5,
  "user_id": 1,
  "configured": true
}
```

---

## RAG API

### POST `/api/v1/rag/query`

RAG-Abfrage durchführen.

**Request:**
```json
{
  "query": "Frage",
  "collection_name": "default",
  "k": 5
}
```

**Response (200):**
```json
{
  "results": ["Ergebnis 1", "Ergebnis 2"],
  "metadata": [
    {"doc_id": "doc_1", "chunk_id": "chunk_1"},
    {"doc_id": "doc_2", "chunk_id": "chunk_2"}
  ]
}
```

---

### POST `/api/v1/rag/add-text`

Text zur Wissensbasis hinzufügen.

**Request:**
```json
{
  "text": "Dokumententext",
  "metadata": {"key": "value"},
  "collection_name": "default"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Text added successfully",
  "ids": ["chunk_1", "chunk_2"]
}
```

---

### POST `/api/v1/rag/create-collection`

Neue Collection erstellen.

**Request:**
```json
{
  "collection_name": "neue_collection"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Collection 'neue_collection' created."
}
```

---

### DELETE `/api/v1/rag/delete-collection`

Collection löschen.

**Request:**
```json
{
  "collection_name": "neue_collection"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Collection 'neue_collection' deleted."
}
```

**Hinweis:** Nicht verfügbar für externes RAG.

---

### GET `/api/v1/rag/list-collections`

Alle Collections auflisten.

**Response (200):**
```json
{
  "collections": ["default", "learning_kb", "documents_kb"]
}
```

---

## Learning API

### POST `/api/v1/learning/match-sent-emails`

Gesendete E-Mails mit Entwürfen abgleichen.

**Response (200):**
```json
{
  "matched": 5,
  "unmatched": 2,
  "report": [...]
}
```

---

### GET `/api/v1/learning/stats`

Learning-Statistiken abrufen.

**Response (200):**
```json
{
  "total_pairs": 100,
  "completed_pairs": 80,
  "avg_rating": 4.5
}
```

---

### GET `/api/v1/learning/pairs`

Alle Learning Pairs auflisten.

**Response (200):**
```json
{
  "pairs": [
    {
      "id": 1,
      "thread_id": "thread_123",
      "draft_message_id": "draft_456",
      "sent_message_id": "sent_789",
      "status": "PAIR_COMPLETED",
      "created_at": "2026-03-01T10:00:00"
    }
  ],
  "count": 100
}
```

---

### DELETE `/api/v1/learning/draft/{draft_id}`

Learning Pair löschen.

**Parameter:**
- `draft_id` (path) — ID des zu löschenden Pairs

**Response (200):**
```json
{
  "success": true,
  "message": "Draft 1 deleted successfully"
}
```

---

## Dashboard API

### GET `/api/v1/dashboard/stats`

Dashboard-Statistiken abrufen.

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "admin"
  },
  "learning": {
    "total_pairs": 100,
    "completed_pairs": 80
  }
}
```

---

### GET `/api/v1/dashboard/conversations`

Letzte Konversationen abrufen.

**Parameter:**
- `limit` (int, default: 10)

**Response (200):**
```json
{
  "conversations": [
    {
      "id": "conv_123",
      "timestamp": "2026-03-01T10:00:00",
      "model_used": "llama3:latest",
      "feedback_score": 4.5
    }
  ],
  "count": 10
}
```

---

### GET `/api/v1/dashboard/email-stats`

E-Mail-Statistiken der letzten N Tage.

**Parameter:**
- `days` (int, default: 30)

**Response (200):**
```json
{
  "daily_counts": [
    {"date": "2026-03-01", "count": 10},
    {"date": "2026-03-02", "count": 15}
  ],
  "total_days": 30
}
```

---

## Configuration API

### GET `/api/v1/config/config`

Aktuelle Konfiguration abrufen.

**Response (200):**
```json
{
  "LLM_PROVIDER": "ollama",
  "LLM_MODEL": "llama3:latest",
  "EMAIL_USER": "user@example.com",
  "DEV_MODE": true,
  ...
}
```

---

### POST `/api/v1/config/config`

Konfiguration speichern.

**Request:**
```json
{
  "LLM_PROVIDER": "openai",
  "LLM_MODEL": "gpt-4",
  ...
}
```

**Response (200):**
```json
{
  "message": "Configuration saved successfully."
}
```

---

### POST `/api/v1/config/config/test`

Verbindungen zu externen Diensten testen.

**Request:**
```json
{
  "EMAIL_USER": "user@example.com",
  "EMAIL_PASSWORD": "password",
  "IMAP_HOST": "imap.example.com",
  ...
}
```

**Response (200):**
```json
[
  {"service": "email", "status": "ok"},
  {"service": "ollama", "status": "ok"},
  {"service": "chromadb", "status": "ok"}
]
```

---

### GET `/api/v1/config/models`

Verfügbare LLM-Modelle abrufen.

**Response (200):**
```json
{
  "models": [
    {"id": "llama3:latest", "name": "Ollama: llama3:latest", "provider": "ollama"},
    {"id": "gpt-4", "name": "OpenAI GPT-4", "provider": "openai"},
    {"id": "claude-3-opus", "name": "Anthropic Claude 3 Opus", "provider": "anthropic"},
    {"id": "gemini-pro", "name": "Google Gemini Pro", "provider": "google"}
  ]
}
```

---

## Services API

### GET `/api/v1/services/status`

Status aller Dienste abrufen.

**Response (200):**
```json
{
  "services": {
    "chromadb": {"status": "running", "port": 38000},
    "ollama": {"status": "running", "port": 11434},
    "redis": {"status": "running", "port": 36379}
  }
}
```

---

### POST `/api/v1/services/restart`

Dienste neu starten.

**Request:**
```json
{
  "service": "chromadb"
}
```

**Response (200):**
```json
{
  "status": "restarting",
  "service": "chromadb"
}
```

---

## Onboarding API

### GET `/api/v1/onboarding/status`

Onboarding-Status abrufen.

**Response (200):**
```json
{
  "completed": false,
  "steps": {
    "email_configured": true,
    "llm_configured": true,
    "first_draft_generated": false
  }
}
```

---

### POST `/api/v1/onboarding/complete`

Onboarding-Schritt als abgeschlossen markieren.

**Request:**
```json
{
  "step": "first_draft_generated"
}
```

**Response (200):**
```json
{
  "success": true
}
```

---

## Statistics API

### GET `/api/v1/statistics/usage`

Nutzungsstatistiken abrufen.

**Response (200):**
```json
{
  "total_queries": 1000,
  "total_tokens": 500000,
  "avg_response_time": 2.5
}
```

---

### GET `/api/v1/statistics/llm`

LLM-Nutzungsstatistiken.

**Response (200):**
```json
{
  "by_model": {
    "llama3:latest": {"queries": 800, "tokens": 400000}
  }
}
```

---

## Cache API

### POST `/api/v1/cache/clear`

Cache leeren.

**Request:**
```json
{
  "cache_type": "embedding"  // oder "query", "all"
}
```

**Response (200):**
```json
{
  "success": true,
  "cleared_keys": 150
}
```

---

### GET `/api/v1/cache/stats`

Cache-Statistiken abrufen.

**Response (200):**
```json
{
  "embedding_cache": {"size": 100, "hits": 500, "misses": 50},
  "query_cache": {"size": 50, "hits": 200, "misses": 20}
}
```

---

## Tasks API

### GET `/api/v1/tasks`

Hintergrundaufgaben auflisten.

**Response (200):**
```json
{
  "tasks": [
    {
      "id": "task_123",
      "type": "ingestion",
      "status": "running",
      "progress": 0.75
    }
  ]
}
```

---

### POST `/api/v1/tasks/cancel/{task_id}`

Aufgabe abbrechen.

**Parameter:**
- `task_id` (path) — Aufgaben-ID

**Response (200):**
```json
{
  "success": true,
  "message": "Task cancelled"
}
```

---

## Evaluation API

### POST `/api/v1/evaluation/evaluate`

RAG-Evaluation durchführen.

**Request:**
```json
{
  "query": "Testfrage",
  "expected_answer": "Erwartete Antwort"
}
```

**Response (200):**
```json
{
  "precision": 0.95,
  "recall": 0.90,
  "f1_score": 0.92
}
```

---

### GET `/api/v1/evaluation/results`

Evaluation-Ergebnisse abrufen.

**Response (200):**
```json
{
  "evaluations": [
    {
      "id": "eval_123",
      "query": "Testfrage",
      "score": 0.92,
      "created_at": "2026-03-01T10:00:00"
    }
  ]
}
```

---

## Fehlerbehandlung

### HTTP-Statuscodes

| Code | Bedeutung | Beschreibung |
|------|-----------|--------------|
| 200 | OK | Anfrage erfolgreich |
| 201 | Created | Ressource erfolgreich erstellt |
| 400 | Bad Request | Ungültige Anfrageparameter |
| 401 | Unauthorized | Nicht authentifiziert |
| 403 | Forbidden | Keine Berechtigung |
| 404 | Not Found | Ressource nicht gefunden |
| 429 | Too Many Requests | Rate Limit überschritten |
| 500 | Internal Server Error | Interner Serverfehler |
| 503 | Service Unavailable | Dienst nicht verfügbar |

### Fehlerantwortformat

```json
{
  "detail": "Fehlermeldung"
}
```

### Spezifische Fehler

**ValidationError (400):**
```json
{
  "detail": "Invalid email address"
}
```

**DocumentNotFoundError (404):**
```json
{
  "detail": "Document 'doc_123' not found in collection 'default'"
}
```

**ServiceUnavailableError (503):**
```json
{
  "detail": "Service 'email' is unavailable: Connection timeout"
}
```

**RateLimitExceeded (429):**
```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds."
}
```

---

## Health Check

### GET `/api/health`

Umfassende Systemprüfung.

**Response (200):**
```json
{
  "status": "healthy",
  "checks": {
    "api": "ok",
    "disk": {
      "status": "ok",
      "free_gb": 50.5
    },
    "ollama": {
      "status": "ok",
      "models_count": 2
    },
    "permissions": {
      "status": "ok",
      "writable_dirs": ["./data"]
    }
  }
}
```

---

## Root

### GET `/`

Root-Informationen.

**Response (200):**
```json
{
  "message": "PantheonMail API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

## Swagger UI

### GET `/docs`

Interaktive Swagger-UI.

**URL:** http://localhost:33800/docs

---

## ReDoc

### GET `/redoc`

Alternative API-Dokumentation.

**URL:** http://localhost:33800/redoc

---

## Lizenz

Dieses Projekt steht unter der AGPL-3.0 Lizenz.
