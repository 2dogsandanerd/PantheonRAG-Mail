# PantheonRAG-Mail — Architektur

> **Hinweis:** Dies ist die **Open-Source Edition** mit Basis-RAG. Für Enterprise-Architektur (Multi-Lane Consensus, Knowledge Graph) siehe [PantheonRAG Enterprise Core v4.0](../planung/manifest_v4.0.md).

## Inhaltsverzeichnis
1. [Architekturübersicht](#architekturübersicht)
2. [Komponentendiagramme](#komponentendiagramme)
3. [Datenflussdiagramme](#datenflussdiagramme)
4. [Deployment-Architektur](#deployment-architektur)
5. [API-Referenz](#api-referenz)
6. [MCP-Integration](#mcp-integration)

---

## Architekturübersicht

PantheonRAG-Mail ist eine modulare Anwendung, die aus zwei Hauptkomponenten besteht:

1. **Email Assistant** - Verwaltet E-Mail-Funktionen und Benutzeroberfläche
2. **RAG Module** - Verwaltet Wissensspeicherung und Abfragen (Basis-RAG mit ChromaDB)

Die modulare Architektur ermöglicht unabhängige Entwicklung, Bereitstellung und Skalierung beider Systeme.

---

## Komponentendiagramme

### Monolithische Architektur (vor v5.0)
```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Electron)                  │
├─────────────────────────────────────────────────────────┤
│                    Backend (FastAPI)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  Email      │  │  Draft      │  │    RAG          │ │
│  │  Service    │  │  Service    │  │   Engine        │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐│
│  │                Datenbank (SQLite)                   ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Modulare Architektur (v5.0+)
```
┌─────────────────┐         ┌─────────────────────────────┐
│   Frontend      │         │        RAG Module           │
│   (Electron)    │         │  (Knowledge-Base-Kit)     │
└─────────┬───────┘         └──────────────┬──────────────┘
          │                                │
    ┌─────▼────────┐              ┌────────▼────────┐
    │ Email        │              │ RAG             │
    │ Assistant    │◄────────────►│ Engine          │
    │ (FastAPI)    │   API/MCP    │ (FastAPI)       │
    └──────────────┘              └─────────────────┘
          │                                │
    ┌─────▼────────┐              ┌────────▼────────┐
    │ Datenbank    │              │ VektorDB        │
    │ (SQLite)     │              │ (ChromaDB)      │
    └──────────────┘              └─────────────────┘
```

### Detailansicht der Hauptkomponenten

#### Email Assistant
```
┌─────────────────────────────────────────────────────────┐
│                    Email Assistant                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  Email      │  │  Draft      │  │  Learning       │ │
│  │  Service    │  │  Service    │  │   Manager       │ │
│  │             │  │             │  │                 │ │
│  │ - IMAP/Gmail│  │ - RAG       │  │ - Korrektur-    │ │
│  │ - Thread    │  │   Integration│  │   lernen       │ │
│  │   Verwaltung│  │ - Prompt    │  │ - Selective     │ │
│  │ - Filter    │  │   Engineering│  │   Spock        │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐│
│  │              Konfigurations-                        ││
│  │              und Abhängigkeits-                     ││
│  │              management                             ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

#### RAG Module
```
┌─────────────────────────────────────────────────────────┐
│                    RAG Module                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  Ingestion  │  │  Query      │  │  Collection     │ │
│  │  Service    │  │  Service    │  │   Manager       │ │
│  │             │  │             │  │                 │ │
│  │ - Docling   │  │ - Hybrid    │  │ - CRUD          │ │
│  │   Integration│  │   Suche     │  │   Operationen   │ │
│  │ - Chunking  │  │ - Reranking │  │ - Metadaten     │ │
│  │ - Indexing  │  │ - Context   │  │   Verwaltung    │ │
│  └─────────────┘  │   Aggregation│  └─────────────────┘ │
│                   └─────────────┘                      │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐│
│  │              Vektor-                               ││
│  │              Speicher-                              ││
│  │              und Abfrage-                           ││
│  │              optimierung                            ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## Datenflussdiagramme

### Antwortgenerierung mit RAG
```
Benutzer-E-Mail
       │
       ▼
   [Email Assistant]
       │
       ├─ Extrahiere Betreff & Inhalt
       ├─ Erstelle Suchanfrage
       ▼
   [RAG Module]
       │
       ├─ Durchsuche relevante Dokumente
       ├─ Wende Hybrid-Suche an (Vektor + BM25)
       ├─ Reranke Ergebnisse (optional)
       ▼
   [Relevante Kontexte]
       │
       ▼
   [Email Assistant]
       │
       ├─ Kombiniere mit Graph-Lite Fakten
       ├─ Erstelle Prompt mit Kontext
       ├─ Sende an LLM
       ▼
   [Generierte Antwort]
       │
       ▼
   [Benutzer sieht Antwort]
```

### Lernzyklus mit Selective Spock
```
Benutzer korrigiert Antwort
       │
       ▼
   [Learning Manager]
       │
       ├─ Speichert Korrekturpaar (Original/Verbessert)
       ├─ Wendet Selective Spock an
       ▼
   [Semantische Chunks]
       │
       ▼
   [RAG Module]
       │
       ├─ Indiziert Chunks in "learning_pairs_kb"
       ├─ Aktualisiert Wissensbasis
       ▼
   [Verbesserte zukünftige Antworten]
```

### MCP-Integration
```
[OpenClaw oder anderer Agent]
       │
       ▼
   [MCP Protokoll]
       │
       ├─ Registriere Tools (query_knowledge, list_collections)
       ▼
   [MCP Server im RAG Module]
       │
       ├─ Wandelt MCP-Anfragen in API-Aufrufe um
       ▼
   [RAG Module API]
       │
       ├─ Führt Abfragen aus
       ├─ Gibt Ergebnisse zurück
       ▼
   [MCP Server]
       │
       ▼
   [Agent mit RAG-Kontext]
```

---

## Deployment-Architektur

### Lokale Entwicklung
```
┌─────────────────────────────────────────────────────────┐
│                    Entwicklungsumgebung                │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐     ┌─────────────────────────────┐   │
│  │   Frontend  │     │        RAG Module           │   │
│  │   (Electron)│     │  (Knowledge-Base-Kit)     │   │
│  │             │     │                           │   │
│  │  localhost: │     │    localhost:8080         │   │
│  │  3000       │     │                           │   │
│  └─────────────┘     └─────────────────────────────┘   │
│         │                        │                     │
│         ▼                        ▼                     │
│  ┌─────────────┐     ┌─────────────────────────────┐   │
│  │ Email       │     │ RAG                         │   │
│  │ Assistant   │     │ Engine                      │   │
│  │ (FastAPI)   │     │ (FastAPI)                   │   │
│  │             │     │                             │   │
│  │ localhost:  │     │   localhost:8081            │   │
│  │ 33800       │     │                             │   │
│  └─────────────┘     └─────────────────────────────┘   │
│         │                        │                     │
│         ▼                        ▼                     │
│  ┌─────────────┐     ┌─────────────────────────────┐   │
│  │ SQLite      │     │ ChromaDB                    │   │
│  │ (lokale DB) │     │ (Vektordatenbank)         │   │
│  └─────────────┘     └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Container-basiertes Deployment
```
┌─────────────────────────────────────────────────────────┐
│                    Docker Deployment                   │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │   Frontend      │    │        RAG Module           │ │
│  │   (Container)   │    │        (Container)        │ │
│  │                 │    │                           │ │
│  │  Port: 3000     │    │    Port: 8080             │ │
│  └─────────┬───────┘    └──────────────┬──────────────┘ │
│            │                           │                │
│    ┌───────▼────────┐        ┌─────────▼────────┐       │
│    │ Email Ass.     │        │ RAG Engine       │       │
│    │ (Container)    │        │ (Container)      │       │
│    │                │        │                  │       │
│    │  Port: 33800   │        │   Port: 8081     │       │
│    └─────────┬──────┘        └─────────┬────────┘       │
│              │                         │                │
│    ┌─────────▼────────┐    ┌───────────▼────────┐       │
│    │ SQLite           │    │ ChromaDB           │       │
│    │ (Volume)         │    │ (Volume)           │       │
│    └──────────────────┘    └────────────────────┘       │
│              │                         │                │
│    ┌─────────▼────────┐    ┌───────────▼────────┐       │
│    │ Redis            │    │ Ollama             │       │
│    │ (Queue/Cache)    │    │ (LLM Service)      │       │
│    └──────────────────┘    └────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

---

## API-Referenz

### Email Assistant API

#### E-Mail Endpunkte
- `GET /api/v1/email/inbox`
  - Parameter: `max_results`, `filter_mode`
  - Antwort: Liste ungelesener E-Mails

- `GET /api/v1/email/thread/{thread_id}`
  - Antwort: Vollständige Thread-Historie

- `POST /api/v1/email/draft`
  - Body: `{sender, subject, body, thread_id, use_rag}`
  - Antwort: Generierter Antwortentwurf mit RAG-Kontext

- `POST /api/v1/email/draft/save`
  - Body: `{to, subject, body, thread_id, in_reply_to}`
  - Antwort: Speicherstatus

#### RAG Integration (wenn lokal)
- `POST /api/v1/rag/query`
  - Body: `{query, collections, k}`
  - Antwort: RAG-Ergebnisse mit Kontext

### RAG Module API

#### Abfrage-Endpunkte
- `POST /api/v1/rag/query`
  - Body: `{query, collections, k, use_reranker}`
  - Antwort: `{answer, sources, context, metadata}`

#### Collection-Endpunkte
- `GET /api/v1/rag/collections`
  - Antwort: Liste verfügbarer Collections

- `POST /api/v1/rag/collections`
  - Body: `{name, embedding_config}`
  - Antwort: Erstellungsstatus

#### Dokumenten-Endpunkte
- `POST /api/v1/rag/documents/upload`
  - Dateiupload: Dokumente zur Indizierung
  - Antwort: Uploadstatus

---

## MCP-Integration

### MCP-Server Konfiguration
Der RAG-Module enthält einen MCP-Server (Model Context Protocol) für Agenten-Integration:

#### Verfügbare Tools
1. `query_knowledge(query, collections?, k?, use_reranker?)`
   - Führt RAG-Abfragen aus
   - Gibt Antwort mit Quellen zurück

2. `list_collections()`
   - Listet verfügbare Collections auf

#### MCP-Server Start
```bash
# Im RAG-Modul Verzeichnis
npm install
npm start
```

#### Agent-Konfiguration
```bash
openclaw mcp add --transport stdio knowledge-kit npx -y @knowledge-kit/mcp-server
```

---

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.