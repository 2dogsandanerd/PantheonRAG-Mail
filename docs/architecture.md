# PantheonMail — Architektur

> **Hinweis:** Dies ist die **Open-Source Edition (Fiat Lean Mode)** mit optimierter Performance. Für Enterprise-Architektur (Multi-Lane Consensus, Knowledge Graph) siehe [PantheonRAG Enterprise Core v4.0](../planung/manifest_v4.0.md).

**Version:** v5.0.0  
**Letzte Aktualisierung:** März 2026

---

## Inhaltsverzeichnis

1. [Architekturübersicht](#architekturübersicht)
2. [Modulare Architektur](#modulare-architektur)
3. [Komponentendiagramme](#komponentendiagramme)
4. [Datenflussdiagramme](#datenflussdiagramme)
5. [Deployment-Architektur](#deployment-architektur)
6. [Service-Architektur](#service-architektur)
7. [Datenbank-Architektur](#datenbank-architektur)
8. [Sicherheitsarchitektur](#sicherheitsarchitektur)

---

## Architekturübersicht

PantheonMail v5.0 ist eine **modulare Anwendung**, die aus zwei Hauptkomponenten besteht:

### 1. Email Assistant (FastAPI Backend)
Verwaltet E-Mail-Funktionen, Benutzeroberfläche und AI-Draft-Generierung:
- **Email Services**: IMAP/Gmail Integration, Thread-Verwaltung, Filter
- **Draft Service**: AI-generierte Antwortentwürfe mit RAG-Kontext
- **Learning Manager**: Speichert Korrekturen und verbessert zukünftige Antworten
- **Health Monitor**: Überwacht alle Dienste (ChromaDB, Ollama, Redis)
- **Config Service**: Hot-Reload-fähige Konfigurationsverwaltung

### 2. RAG Module (Optional, Knowledge-Base-Kit)
Verwaltet Wissensspeicherung und Abfragen (kann auch intern im Backend laufen):
- **Ingestion Service**: Dokumentenverarbeitung mit Docling
- **Query Service**: Hybrid-Suche (Vektor + BM25)
- **Collection Manager**: CRUD-Operationen für Collections
- **Graph-Lite Service**: SQLite-basierte Entity-Relations

### 3. Frontend (Electron + React)
Desktop-Oberfläche für Benutzerinteraktion:
- **React 19.2**: Komponentenbasierte UI
- **Material-UI 5.18**: Design-System
- **Electron 38.2**: Cross-Platform Desktop-App

---

## Modulare Architektur

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

**Nachteile:**
- Alle Komponenten in einem Container
- Schwer zu skalieren
- Gemeinsame Ressourcennutzung

### Modulare Architektur (v5.0+)

```
┌─────────────────┐         ┌─────────────────────────────┐
│   Frontend      │         │        RAG Module           │
│   (Electron)    │         │  (Knowledge-Base-Kit)       │
│   localhost:    │         │  localhost:8080             │
│   3000          │         │                             │
└────────┬────────┘         └──────────────┬──────────────┘
         │                                 │
         │ REST API + WebSocket            │ REST API / MCP
         │                                 │
   ┌─────▼────────┐              ┌─────────▼────────┐
   │ Email        │              │ RAG              │
   │ Assistant    │◄────────────►│ Engine           │
   │ (FastAPI)    │   API/MCP    │ (FastAPI)        │
   │ localhost:   │              │ localhost:8081   │
   │ 33800        │              │                  │
   └─────┬────────┘              └─────────┬────────┘
         │                                 │
   ┌─────▼────────┐              ┌─────────▼────────┐
   │ Datenbank    │              │ VektorDB         │
   │ (SQLite)     │              │ (ChromaDB)       │
   │ app.db       │              │ :38000           │
   └──────────────┘              └──────────────────┘
         │
   ┌─────▼────────┐
   │ Redis        │
   │ (Cache/Queue)│
   │ :36379       │
   └──────────────┘
```

**Vorteile:**
- Unabhängige Entwicklung und Skalierung
- RAG-Modul kann von anderen Apps genutzt werden
- Bessere Ressourcentrennung
- Einfacheres Testing

---

## Komponentendiagramme

### Email Assistant - Detailansicht

```
┌─────────────────────────────────────────────────────────────┐
│                    Email Assistant (FastAPI)                │
├─────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI Routers)                                │
│  ┌────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐ ┌────────┐ │
│  │ /auth  │ │ /email │ │ /draft  │ │ /learning│ │ /rag   │ │
│  │        │ │        │ │         │ │          │ │        │ │
│  │ Login  │ │ Inbox  │ │ Generate│ │ Pairs   │ │ Query  │ │
│  │ Register│ │ Thread │ │ Save   │ │ Spock   │ │ Config │ │
│  │ Refresh│ │ Filter │ │ Delete │ │ Rating  │ │ Status │ │
│  └────────┘ └────────┘ └─────────┘ └──────────┘ └────────┘ │
│                                                             │
│  Service Layer                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Email        │  │ Draft        │  │ Learning        │  │
│  │ Service      │  │ Service      │  │ Manager         │  │
│  │              │  │              │  │                 │  │
│  │ • IMAPClient │  │ • RAG        │  │ • Draft-Sent   │  │
│  │ • Gmail      │  │   Integration│  │   Pairs        │  │
│  │ • OAuth2     │  │ • Prompt     │  │ • Selective    │  │
│  │ • SSL/TLS    │  │   Engineering│  │   Spock        │  │
│  │ • SSL/TLS    │  │ • LLM Call   │  │ • Feedback     │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Config       │  │ Health       │  │ Onboarding      │  │
│  │ Service      │  │ Monitor      │  │ Service         │  │
│  │              │  │              │  │                 │  │
│  │ • Hot-Reload │  │ • Service    │  │ • Wizard        │  │
│  │ • .env       │  │   Checks     │  │ • Setup         │  │
│  │ • Validation │  │ • Alerts     │  │ • Validation    │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                             │
│  Core Infrastructure                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Auth (JWT)   │  │ Database     │  │ Rate Limiter    │  │
│  │              │  │ (SQLAlchemy) │  │                 │  │
│  │ • Access     │  │ • Async      │  │ • SlowAPI       │  │
│  │ • Refresh    │  │ • SQLite     │  │ • Redis         │  │
│  │ • Rotation   │  │ • Models     │  │ • Limits        │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### RAG Module - Detailansicht

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Module (FastAPI)                     │
├─────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI Routers)                                │
│  ┌────────────┐ ┌────────────┐ ┌─────────────────┐         │
│  │ /query     │ │ /collections│ │ /documents      │         │
│  │            │ │             │ │                 │         │
│  │ POST /query│ │ GET   List  │ │ POST /upload    │         │
│  │ GET  status│ │ POST  Create│ │ GET   status    │         │
│  │            │ │ DELETE Delete│ │ GET   analysis │         │
│  └────────────┘ └────────────┘ └─────────────────┘         │
│                                                             │
│  Service Layer                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Ingestion    │  │ Query        │  │ Collection      │  │
│  │ Service      │  │ Service      │  │ Manager         │  │
│  │              │  │              │  │                 │  │
│  │ • Docling    │  │ • Hybrid     │  │ • CRUD          │  │
│  │   Parsing    │  │   Suche      │  │ • Metadata      │  │
│  │ • Chunking   │  │ • Vektor     │  │ • Permissions   │  │
│  │ • Embedding  │  │ • BM25       │  │                 │  │
│  │ • Indexing   │  │ • Reranking  │  │                 │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Graph-Lite   │  │ Selective    │  │ MCP Server      │  │
│  │ Service      │  │ Spock        │  │                 │  │
│  │              │  │              │  │                 │  │
│  │ • SQLite     │  │ • Semantic   │  │ • Tools         │  │
│  │   Facts      │  │   Chunking   │  │ • query_knowledge│ │
│  │ • Entity-    │  │ • Learning   │  │ • list_collections││
│  │   Relations  │  │   Pairs      │  │                 │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                             │
│  Storage Layer                                              │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ ChromaDB     │  │ File Storage │                         │
│  │ (Vectors)    │  │ (Uploads)    │                         │
│  │              │  │              │                         │
│  │ • Collections│  │ • PDF        │                         │
│  │ • Embeddings │  │ • DOCX       │                         │
│  │ • Metadata   │  │ • XLSX       │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### Frontend - Komponentenarchitektur

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Electron + React)              │
├─────────────────────────────────────────────────────────────┤
│  Electron Main Process                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Window       │  │ IPC          │  │ Auto-Update     │  │
│  │ Manager      │  │ Handler      │  │ (geplant)       │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                             │
│  React Renderer Process                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ App.jsx                                               │  │
│  │ • Auth Gate (Login/Logout)                            │  │
│  │ • Route Management                                    │  │
│  │ • Global State (Auth, Config)                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Feature Components                                         │
│  ┌────────────┐ ┌────────────┐ ┌──────────┐ ┌───────────┐ │
│  │ Inbox      │ │ Draft      │ │ RAG      │ │ Dashboard │ │
│  │            │ │            │ │          │ │           │ │
│  │ • Email    │ │ • Generate │ │ • Upload │ │ • Stats   │ │
│  │   List     │ │ • Edit     │ │ • Search │ │ • Health  │ │
│  │ • Filter   │ │ • Save     │ │ • Query  │ │ • Usage   │ │
│  │ • Thread   │ │ • Delete   │ │ • Config │ │           │ │
│  └────────────┘ └────────────┘ └──────────┘ └───────────┘ │
│                                                             │
│  Shared Components                                          │
│  ┌────────────┐ ┌────────────┐ ┌──────────┐ ┌───────────┐ │
│  │ LoginForm  │ │ Header     │ │ Settings │ │ Toast     │ │
│  │            │ │            │ │          │ │           │ │
│  │ • Register │ │ • Nav      │ │ • LLM    │ │ • Success │ │
│  │ • Login    │ │ • User     │ │ • Email  │ │ • Error   │ │
│  │ • Logout   │ │ • Status   │ │ • System │ │ • Info    │ │
│  └────────────┘ └────────────┘ └──────────┘ └───────────┘ │
│                                                             │
│  API Layer                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Axios        │  │ Auth         │  │ Error           │  │
│  │ Client       │  │ Interceptor  │  │ Handler         │  │
│  │              │  │              │  │                 │  │
│  │ • Base URL   │  │ • Token      │  │ • 401 Refresh   │  │
│  │ • Timeout    │  │ • Auto-      │  │ • Retry Logic   │  │
│  │ • Headers    │  │   Refresh    │  │ • Toast         │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Datenflussdiagramme

### 1. Antwortgenerierung mit RAG

```
┌──────────────┐
│ Benutzer     │
│ öffnet E-Mail│
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Frontend (Electron)                    │
│  • Zeigt E-Mail-Inhalt                  │
│  • "Generate Draft" Button              │
└──────┬──────────────────────────────────┘
       │ POST /api/v1/email/draft
       │ {sender, subject, body, thread_id, use_rag: true}
       ▼
┌─────────────────────────────────────────┐
│  Email Assistant (FastAPI)              │
│  1. Validiere Request                   │
│  2. Extrahiere E-Mail-Daten             │
└──────┬──────────────────────────────────┘
       │
       ├─────────────────────────┐
       │                         │
       ▼                         ▼
┌──────────────┐        ┌─────────────────┐
│ Draft        │        │ RAG Module      │
│ Service      │        │ (optional)      │
│              │        │                 │
│ • Prompt     │◄───────┤ 1. Query        │
│   erstellen  │        │    Suche        │
│ • LLM Call   │        │ 2. Hybrid       │
│              │        │    (Vektor+BM25)│
└──────┬───────┘        │ 3. Reranking    │
       │                │ 4. Kontext      │
       │                │    aggregieren  │
       │                └─────────────────┘
       │                         │
       │◄────────────────────────┘
       │ RAG-Kontext
       ▼
┌──────────────┐
│ LLM Provider │
│ (Ollama/     │
│ OpenAI/      │
│ Gemini)      │
│              │
│ • System     │
│   Prompt     │
│ • E-Mail +   │
│   Kontext    │
│ • Antwort    │
│   generieren │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Generierte   │
│ Antwort      │
│              │
│ • Draft      │
│   anzeigen   │
│ • Editieren  │
│ • Speichern  │
└──────────────┘
```

### 2. Lernzyklus mit Selective Spock

```
┌──────────────┐
│ Benutzer     │
│ korrigiert   │
│ Antwort      │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Frontend speichert Korrektur           │
│  • Original (AI-Draft)                  │
│  • Verbessert (Benutzer-Edit)           │
└──────┬──────────────────────────────────┘
       │ POST /api/v1/learning/pair
       ▼
┌─────────────────────────────────────────┐
│  Learning Manager                       │
│  1. LearningPair erstellen              │
│  2. Status: PAIR_COMPLETED              │
│  3. Selective Spock auslösen            │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Selective Spock Chunking               │
│  • Analysiere Korrekturpaar             │
│  • Identifiziere semantische Blöcke     │
│  • Erstelle Chunks mit Kontext          │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  RAG Module                             │
│  • Indiziere Chunks in "learning_kb"    │
│  • Verknüpfe mit Metadata               │
│  • Mache für zukünftige Queries         │
│    verfügbar                            │
└──────┬──────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ Zukünftige   │
│ Antworten    │
│ verwenden    │
│ gelerntes    │
│ Wissen       │
└──────────────┘
```

### 3. JWT-Authentifizierungsfluss

```
┌──────────────┐
│ Benutzer     │
│ startet App  │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  App.jsx (Frontend)                     │
│  • checkAuth() im useEffect             │
│  • authLoading = true                   │
└──────┬──────────────────────────────────┘
       │ GET /api/v1/auth/me
       │ Authorization: Bearer <token>
       ▼
┌─────────────────────────────────────────┐
│  Backend (FastAPI)                      │
│  • JWT validieren                       │
│  • User aus DB laden                    │
└──────┬──────────────────────────────────┘
       │
       ├──────────────┬──────────────┐
       │              │              │
       ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Token    │  │ Token    │  │ DEV_MODE │
│ gültig   │  │ ungültig │  │ = true   │
│          │  │ (401)    │  │          │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │              │
     │             ▼              │
     │      ┌──────────────┐     │
     │      │ Auto-Refresh │     │
     │      │ versuchen    │     │
     │      └──────┬───────┘     │
     │             │              │
     │             ├──────┬──────┤
     │             │      │      │
     │             ▼      ▼      ▼
     │      ┌────────┐ ┌──────┐ ┌────────┐
     │      │ Erfolg │ │ Fail │ │ Dummy  │
     │      │        │ │      │ │ User   │
     │      │ Neuer  │ │      │ │        │
     │      │ Token  │ │      │ │ Alle   │
     │      │        │ │      │ │ End-   │
     │      │        │ │      │ │ points │
     │      │        │ │      │ │ frei   │
     │      │        │ │      │ │        │
     │      └───┬────┘ └──┬───┘ └───┬────┘
     │          │         │         │
     ▼          ▼         ▼         ▼
┌─────────────────────────────────────────┐
│  isAuthenticated = true/false           │
│  • Loading = false                      │
│  • Zeige Haupt-UI oder Login            │
└─────────────────────────────────────────┘
```

---

## Deployment-Architektur

### Lokale Entwicklung (ohne Docker)

```
┌────────────────────────────────────────────────────────────┐
│                   Entwicklungsumgebung                     │
├────────────────────────────────────────────────────────────┤
│  ┌──────────────┐                                          │
│  │   Frontend   │                                          │
│  │   (npm start)│                                          │
│  │              │                                          │
│  │  localhost:  │                                          │
│  │  3000        │                                          │
│  └──────┬───────┘                                          │
│         │                                                  │
│         │ REST API                                         │
│         ▼                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Backend      │    │ Ollama       │    │ ChromaDB     │ │
│  │ (uvicorn)    │    │ (system)     │    │ (Docker)     │ │
│  │              │    │              │    │              │ │
│  │  localhost:  │    │  localhost:  │    │  localhost:  │ │
│  │  33800       │    │  11434       │    │  38000       │ │
│  └──────┬───────┘    └──────────────┘    └──────────────┘ │
│         │                                                  │
│         ▼                                                  │
│  ┌──────────────┐    ┌──────────────┐                     │
│  │ SQLite       │    │ Redis        │                     │
│  │ (app.db)     │    │ (Docker)     │                     │
│  │              │    │              │                     │
│  │  ./data/     │    │  localhost:  │                     │
│  │  app.db      │    │  36379       │                     │
│  └──────────────┘    └──────────────┘                     │
└────────────────────────────────────────────────────────────┘
```

### Container-basiertes Deployment (docker-compose)

```
┌────────────────────────────────────────────────────────────┐
│                   Docker Deployment                        │
├────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌──────────────────────────────┐  │
│  │   Frontend      │    │        RAG Module            │  │
│  │   (Container)   │    │        (Container)           │  │
│  │                 │    │                              │  │
│  │  Port: 3000     │    │    Port: 8080                │  │
│  └─────────┬───────┘    └───────────────┬──────────────┘  │
│            │                            │                 │
│    ┌───────▼────────┐        ┌──────────▼────────┐       │
│    │ Email Ass.     │        │ RAG Engine        │       │
│    │ (Container)    │        │ (Container)       │       │
│    │                │        │                   │       │
│    │  Port: 33800   │        │   Port: 8081      │       │
│    └─────────┬──────┘        └─────────┬─────────┘       │
│              │                         │                 │
│    ┌─────────▼────────┐    ┌───────────▼────────┐       │
│    │ SQLite           │    │ ChromaDB           │       │
│    │ (Volume)         │    │ (Volume)           │       │
│    └──────────────────┘    └────────────────────┘       │
│              │                         │                 │
│    ┌─────────▼────────┐    ┌───────────▼────────┐       │
│    │ Redis            │    │ Ollama             │       │
│    │ (Queue/Cache)    │    │ (LLM Service)      │       │
│    └──────────────────┘    └────────────────────┘       │
└────────────────────────────────────────────────────────────┘
```

### Netzwerk-Topologie

```
┌──────────────────────────────────────────────────────────┐
│                  Docker Networks                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  rag_network (172.20.0.0/16)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ rag_module   │  │ rag_chromadb │  │ email_assist │  │
│  │ :8080        │  │ :8000        │  │ :33800       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  email_network (172.21.0.0/16)                          │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ email_assist │  │ redis        │                     │
│  │ :33800       │  │ :6379        │                     │
│  └──────────────┘  └──────────────┘                     │
│                                                          │
│  Host-Zugriff (Port Mapping)                            │
│  • 33800:33800 → Backend API                            │
│  • 8080:8080   → RAG Module API                         │
│  • 38000:8000  → ChromaDB                               │
│  • 36379:6379  → Redis                                  │
│  • 11434:11434 → Ollama (shared)                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Service-Architektur

### Backend Services (FastAPI)

| Service | Datei | Beschreibung |
|---------|-------|--------------|
| **Email Service** | `src/core/email_clients/` | IMAP/Gmail Client, SSL/TLS, OAuth2 |
| **Draft Service** | `src/services/draft_service.py` | AI-Draft-Generierung mit RAG |
| **Learning Manager** | `src/services/learning_manager.py` | Learning Pairs, Selective Spock |
| **Config Service** | `src/services/config_service.py` | Hot-Reload-Konfiguration (.env) |
| **Health Monitor** | `src/services/health_monitor.py` | Service-Überwachung, Alerts |
| **Onboarding Service** | `src/services/onboarding_service.py` | Setup-Wizard, Validierung |
| **Analytics Service** | `src/services/analytics_service.py` | Statistiken, Tracking |
| **External RAG Connector** | `src/services/external_rag_connector.py` | Proxy zu externem RAG |

### RAG Services (Knowledge-Base-Kit)

| Service | Datei | Beschreibung |
|---------|-------|--------------|
| **Ingestion Service** | `src/services/ingest/` | Docling, Chunking, Embedding |
| **Query Service** | `src/services/query.py` | Hybrid-Suche, Reranking |
| **Collection Manager** | `src/core/collection_manager.py` | CRUD, Metadata |
| **Graph-Lite Service** | `src/services/graph_lite_service.py` | SQLite Facts |
| **MCP Server** | `mcp-server/` | Model Context Protocol |

### Frontend Services (React)

| Service | Datei | Beschreibung |
|---------|-------|--------------|
| **Auth Service** | `src/api/auth.js` | Login, Token-Management, Refresh |
| **Email API** | `src/api/email.js` | Inbox, Drafts, Threads |
| **RAG API** | `src/api/rag.js` | Upload, Query, Collections |
| **Config API** | `src/api/config.js` | Settings, System-Config |

---

## Datenbank-Architektur

### SQLite Schema (Metadaten)

```sql
-- Users (Authentifizierung)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    hashed_password VARCHAR(255),
    is_active BOOLEAN,
    tenant_id INTEGER,
    role VARCHAR(20),
    created_at DATETIME
);

-- Email Accounts (Konfiguration)
CREATE TABLE email_accounts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    account_name VARCHAR(100),
    email_address VARCHAR(255),
    provider VARCHAR(50),
    config TEXT,  -- JSON
    is_default BOOLEAN,
    created_at DATETIME
);

-- Learning Pairs (Feedback)
CREATE TABLE learning_pairs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    thread_id VARCHAR(255),
    draft_message_id VARCHAR(255),
    draft_content TEXT,
    sent_message_id VARCHAR(255),
    sent_content TEXT,
    status VARCHAR(50),
    rating FLOAT,
    created_at DATETIME
);

-- Tenants (Multi-Tenancy)
CREATE TABLE tenants (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    display_name VARCHAR(255),
    subscription_tier VARCHAR(20),
    subscription_status VARCHAR(20),
    max_collections INTEGER,
    max_queries_per_day INTEGER,
    features JSON,
    created_at DATETIME
);

-- Settings (Key-Value)
CREATE TABLE settings (
    key VARCHAR(64) PRIMARY KEY,
    value TEXT
);
```

### ChromaDB Collections (Vektoren)

```
Collections:
├── default (Standard-Wissensbasis)
├── learning_kb (Learning Pairs)
├── documents_kb (Hochgeladene Dokumente)
└── ... (benutzerdefinierte Collections)

Jede Collection:
├── Vektor-Embeddings (nomic-embed-text)
├── Metadata (doc_id, chunk_id, created_at)
└── Content (Text-Chunks)
```

### Graph-Lite Facts (SQLite)

```sql
-- Entity-Relations (statt Neo4j)
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

-- Beispiele:
-- (Person, "Max Mustermann", "arbeitet_für", "Firma", "ACME GmbH", 0.95, "doc_123")
-- (Projekt, "Alpha", "hat_Budget", "Budget", "100000", 0.98, "doc_456")
```

---

## Sicherheitsarchitektur

### JWT-Authentifizierung

```
┌─────────────────────────────────────────┐
│  Token-Struktur                         │
├─────────────────────────────────────────┤
│  Access Token (30 Minuten)              │
│  • Header (alg, typ)                    │
│  • Payload (sub, exp, role)             │
│  • Signature (HS256)                    │
│                                         │
│  Refresh Token (7 Tage)                 │
│  • Einmalige Verwendung                 │
│  • Rotation bei jedem Refresh           │
│  • Speicherung in DB (Hash)             │
└─────────────────────────────────────────┘
```

### Rate Limiting

```python
# SlowAPI Integration
RATE_LIMITS = {
    "default": "100/minute",
    "auth": "10/minute",      # Login/Register
    "email": "30/minute",     # Email-Operationen
    "rag": "50/minute",       # RAG-Queries
    "upload": "10/minute"     # Datei-Uploads
}
```

### CORS-Konfiguration

```python
# development (Electron)
allow_origins=["*"]  # localhost ports

# production
allow_origins=[
    "http://localhost:3000",
    "app://pantheonmail"
]
```

---

## Lizenz

Dieses Projekt steht unter der AGPL-3.0 Lizenz.
