# PantheonRAG-Mail — API Referenz

> **Hinweis:** Dies ist die **Open-Source Edition**. Für Enterprise-APIs siehe [PantheonRAG Enterprise Core v4.0](../planung/manifest_v4.0.md).

## Inhaltsverzeichnis
1. [Email Assistant API](#email-assistant-api)
2. [RAG Module API](#rag-module-api)
3. [MCP Integration API](#mcp-integration-api)
4. [Konfigurationsoptionen](#konfigurationsoptionen)

---

## Email Assistant API

### Root Endpunkt
- **GET /** - Root-Informationen
  - Antwort: `{"message": "Gmail RAG Assistant API", "version": "1.0.0", "docs": "/docs"}`

### Health Check
- **GET /api/health** - Systemgesundheit prüfen
  - Antwort:
    ```json
    {
      "status": "healthy",
      "checks": {
        "api": "ok",
        "disk": {...},
        "ollama": {...},
        "permissions": {...}
      }
    }
    ```

### E-Mail Endpunkte

#### Inbox abrufen
- **GET /api/v1/email/inbox**
  - Parameter:
    - `max_results` (int, default: 10) - Maximale Anzahl an E-Mails
    - `filter_mode` (string, default: "none") - Filtermodus ("none", "auto")
  - Antwort:
    ```json
    {
      "emails": [...],
      "count": 5,
      "user_id": 1,
      "configured": true
    }
    ```

#### Thread-Historie abrufen
- **GET /api/v1/email/thread/{thread_id}**
  - Pfadparameter:
    - `thread_id` - ID des Threads
  - Antwort:
    ```json
    {
      "thread": [...],
      "thread_id": "thread123"
    }
    ```

#### Antwortentwurf generieren
- **POST /api/v1/email/draft**
  - Body:
    ```json
    {
      "sender": "sender@example.com",
      "subject": "Betreff",
      "body": "E-Mail-Text",
      "thread_id": "thread123",
      "use_rag": true
    }
    ```
  - Antwort:
    ```json
    {
      "draft": "Generierte Antwort",
      "no_answer_needed": false,
      "rag_context": "RAG-Kontext",
      "rag_status": "success",
      "rag_collection_count": 2,
      "rag_result_count": 5
    }
    ```

#### Entwurf speichern
- **POST /api/v1/email/draft/save**
  - Body:
    ```json
    {
      "to": "empfaenger@example.com",
      "subject": "Betreff",
      "body": "Antworttext",
      "thread_id": "thread123",
      "in_reply_to": "message123"
    }
    ```
  - Antwort:
    ```json
    {
      "draft_id": "draft123",
      "status": "created",
      "provider": "IMAPClient"
    }
    ```

#### Entwürfe auflisten
- **GET /api/v1/email/drafts**
  - Parameter:
    - `status` (string, optional) - Filter nach Status
    - `limit` (int, default: 50) - Maximale Anzahl
  - Antwort:
    ```json
    {
      "drafts": [...]
    }
    ```

#### Entwurf löschen
- **DELETE /api/v1/email/draft/{draft_id}**
  - Pfadparameter:
    - `draft_id` - ID des zu löschenden Entwurfs
  - Antwort:
    ```json
    {
      "success": true,
      "message": "Draft deleted."
    }
    ```

### Auto-Draft Endpunkte

#### Auto-Draft starten
- **POST /api/v1/auto-draft/start**
  - Antwort:
    ```json
    {
      "status": "started",
      "interval": 300,
      "worker_id": 12345
    }
    ```

#### Auto-Draft stoppen
- **POST /api/v1/auto-draft/stop**
  - Antwort: `{"status": "stopped"}`

#### Auto-Draft Status
- **GET /api/v1/auto-draft/status**
  - Antwort:
    ```json
    {
      "status": "running",
      "started_at": "...",
      "check_interval": 300,
      "worker_id": 12345
    }
    ```

### Konfiguration Endpunkte

#### Systemkonfiguration
- **GET /api/v1/config** - Systemkonfiguration abrufen
- **POST /api/v1/config** - Systemkonfiguration aktualisieren
- **POST /api/v1/config/test** - Konfigurationsvalidierung

### Dienste Endpunkte

#### Dienste Status
- **GET /api/v1/services/status** - Status aller Dienste abrufen
- **POST /api/v1/services/restart** - Dienste neu starten

### Dashboard Endpunkte

#### Dashboard Statistiken
- **GET /api/v1/dashboard/stats** - Dashboard-Statistiken abrufen
- **GET /api/v1/dashboard/emails** - E-Mail-Statistiken
- **GET /api/v1/dashboard/usage** - Nutzungsinformationen

---

## RAG Module API

### Root Endpunkt
- **GET /** - RAG-Modul Information
  - Antwort: `{"message": "Knowledge Base Self-Hosting Kit", "version": "1.2.0", "docs": "/docs"}`

### Health Check
- **GET /health** - RAG-Modul Gesundheit
  - Antwort: `{"status": "healthy"}`

### RAG Query Endpunkte

#### Abfrage durchführen
- **POST /api/v1/rag/query**
  - Body:
    ```json
    {
      "query": "Frage",
      "collections": ["collection1", "collection2"],
      "k": 5,
      "use_reranker": false
    }
    ```
  - Antwort:
    ```json
    {
      "answer": "Antwort",
      "sources": [...],
      "context": [...],
      "metadata": {
        "collections_queried": [...],
        "success": true,
        "error": null,
        "final_k": 5
      }
    }
    ```

### Collections Endpunkte

#### Collections auflisten
- **GET /api/v1/rag/collections**
  - Antwort:
    ```json
    {
      "collections": [
        {"name": "collection1", "count": 100},
        {"name": "collection2", "count": 50}
      ]
    }
    ```

#### Collection erstellen
- **POST /api/v1/rag/collections**
  - Body:
    ```json
    {
      "name": "neue_collection",
      "embedding_config": {
        "provider": "ollama",
        "model": "nomic-embed-text:latest"
      }
    }
    ```
  - Antwort: `{"success": true, "data": {...}}`

#### Collection löschen
- **DELETE /api/v1/rag/collections/{name}**
  - Antwort: `{"success": true}`

### Dokumente Endpunkte

#### Dokument hochladen
- **POST /api/v1/rag/documents/upload**
  - Form-Data:
    - `file` - Hochzuladende Datei
    - `collection_name` - Zielcollection
  - Antwort: `{"success": true, "document_id": "..."}`

#### Dokumente indizieren
- **POST /api/v1/rag/documents/index**
  - Body:
    ```json
    {
      "documents": [
        {
          "text": "Dokumententext",
          "metadata": {"key": "value"},
          "doc_id": "id123"
        }
      ],
      "collection_name": "collection1"
    }
    ```
  - Antwort: `{"success": true, "indexed_count": 1}`

---

## MCP Integration API

### MCP-Server Endpunkte

Der RAG-Module enthält einen MCP-Server (Model Context Protocol) für Agenten-Integration:

#### Verfügbare MCP-Tools

1. **`query_knowledge`**
   - Beschreibung: Führt RAG-Abfragen aus
   - Parameter:
     - `query` (string) - Die Frage oder Suchanfrage
     - `collections` (array, optional) - Liste der zu durchsuchenden Collections
     - `k` (number, optional, default: 5) - Anzahl der Ergebnisse
     - `use_reranker` (boolean, optional, default: true) - Ob Reranking verwendet werden soll
   - Rückgabe: Antworttext mit Quellen

2. **`list_collections`**
   - Beschreibung: Listet verfügbare Collections auf
   - Parameter: Keine
   - Rückgabe: Liste der Collections mit Dokumentanzahl

#### MCP-Server Konfiguration

Der MCP-Server liest seine Konfiguration aus Umgebungsvariablen:

- `KNOWLEDGE_BASE_API_URL` - URL des RAG-Moduls (Standard: `http://localhost:8080`)
- `KNOWLEDGE_BASE_TIMEOUT` - Timeout für Anfragen in Millisekunden (Standard: `120000`)
- `LOG_LEVEL` - Log-Level (Standard: `INFO`)

#### MCP-Server Start

Um den MCP-Server zu starten:

```bash
cd rag_modul/Knowledge-Base-Self-Hosting-Kit/mcp-server
npm install
npm run build
npm start
```

#### Agent-Konfiguration

Um einen Agenten mit dem MCP-Server zu verbinden:

```bash
openclaw mcp add --transport stdio knowledge-kit npx -y @knowledge-kit/mcp-server
```

---

## Konfigurationsoptionen

### Email Assistant Konfiguration

#### Allgemeine Einstellungen
- `MAIL_EDITION_LEAN` (boolean) - Aktiviert Lean-Modus Optimierungen
- `EDITION` (string) - Edition ("developer", "team", "enterprise")

#### Externe RAG-Konfiguration
- `EXTERNAL_RAG_ENABLED` (boolean) - Schaltet externe RAG-Nutzung ein/aus
- `EXTERNAL_RAG_URL` (string) - URL des externen RAG-Moduls
- `EXTERNAL_RAG_API_KEY` (string, optional) - API-Key für authentifizierte Verbindungen
- `EXTERNAL_RAG_TIMEOUT` (int) - Timeout für externe RAG-Anfragen in Sekunden

#### Datenbank-Konfiguration
- `DATABASE_URL` (string) - Datenbankverbindung (z.B. `sqlite:///./data/app.db`)

#### LLM-Konfiguration
- `LLM_PROVIDER` (string) - LLM-Provider ("ollama", "openai", "gemini", "anthropic")
- `LLM_MODEL` (string) - Zu verwendendes LLM-Modell
- `EMBEDDING_PROVIDER` (string) - Embedding-Provider
- `EMBEDDING_MODEL` (string) - Zu verwendendes Embedding-Modell

#### Infrastruktur-Konfiguration
- `CHROMA_HOST` (string) - ChromaDB Host
- `CHROMA_PORT` (int) - ChromaDB Port
- `REDIS_HOST` (string) - Redis Host
- `REDIS_PORT` (int) - Redis Port
- `OLLAMA_HOST` (string) - Ollama Host

#### RAG-Konfiguration
- `RERANKER_ENABLED` (boolean) - Aktiviert Reranking
- `USE_PARENT_RETRIEVER` (boolean) - Verwendet Parent-Retriever
- `USE_ADVANCED_PIPELINE` (boolean) - Verwendet erweiterte RAG-Pipeline

#### E-Mail-Konfiguration
- `EMAIL_PROVIDER` (string) - E-Mail-Provider ("imap", "gmail")
- `EMAIL_USER` (string) - E-Mail-Benutzername
- `EMAIL_PASSWORD` (string) - E-Mail-Passwort
- `EMAIL_SERVER` (string) - E-Mail-Server
- `EMAIL_PORT` (int) - E-Mail-Port

#### WebSocket-Konfiguration
- `WEBSOCKET_HEARTBEAT_INTERVAL` (int) - Heartbeat-Intervall in Sekunden
- `WEBSOCKET_HEARTBEAT_TIMEOUT` (int) - Heartbeat-Timeout in Sekunden
- `WEBSOCKET_AUTH_REQUIRED` (boolean) - Erfordert Authentifizierung
- `WEBSOCKET_LOCALHOST_ONLY` (boolean) - Nur localhost-Zugriff
- `WEBSOCKET_IDLE_TIMEOUT` (int) - Idle-Timeout in Sekunden
- `WEBSOCKET_MAX_QUEUE_SIZE` (int) - Maximale Queue-Größe

#### Health Monitor-Konfiguration
- `HEALTH_CHECK_INTERVAL` (int) - Prüfintervall in Sekunden
- `HEALTH_EVENT_DEBOUNCE` (int) - Event-Debounce-Zeit in Sekunden
- `HEALTH_MAX_SUBSCRIBERS` (int) - Maximale Anzahl an Subscribern

### RAG Module Konfiguration

#### Allgemeine RAG-Konfiguration
- `PORT` (int) - Externer Port (Standard: 8080)
- `DOCS_DIR` (string) - Host-Pfad für Ordner-Ingestion (Standard: `./data/docs`)
- `LLM_PROVIDER` (string) - LLM-Provider
- `LLM_MODEL` (string) - LLM-Modell
- `EMBEDDING_PROVIDER` (string) - Embedding-Provider
- `EMBEDDING_MODEL` (string) - Embedding-Modell
- `CHUNK_SIZE` (int) - Dokument-Chunkgröße (Standard: 512)
- `CHUNK_OVERLAP` (int) - Chunk-Überlappung (Standard: 128)
- `DEBUG` (boolean) - Aktiviert Debug-Logging (Standard: false)
- `LOG_LEVEL` (string) - Log-Level ("DEBUG", "INFO", "WARN", "ERROR")

#### OpenAI-kompatible Server
Für OpenAI-kompatible Server:
- `LLM_PROVIDER=openai_compatible`
- `OPENAI_BASE_URL` - Basis-URL des kompatiblen Servers

---

## Fehlercodes und Behandlung

### HTTP-Statuscodes

- `200 OK` - Anfrage erfolgreich
- `400 Bad Request` - Ungültige Anfrageparameter
- `401 Unauthorized` - Nicht authentifiziert
- `404 Not Found` - Ressource nicht gefunden
- `500 Internal Server Error` - Interner Serverfehler
- `501 Not Implemented` - Funktion nicht implementiert
- `503 Service Unavailable` - Dienst nicht verfügbar

### Fehlerantwortformat

Alle Fehlerantworten folgen diesem Format:

```json
{
  "detail": "Fehlermeldung"
}
```

---

## Authentifizierung

Die API verwendet eine Dummy-Authentifizierung für die Beta-Version. In zukünftigen Versionen wird JWT-basierte Authentifizierung implementiert.

---

## Rate Limiting

Derzeit ist kein Rate Limiting implementiert. In produktiven Umgebungen sollte dies entsprechend konfiguriert werden.

---

## Versionierung

Die API verwendet keine Versionsnummer im Pfad, da es sich um eine interne API handelt. Breaking Changes werden in neuen Major-Versionen veröffentlicht.