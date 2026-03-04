# PantheonMail — Dokumentation

Willkommen zur Dokumentation von **PantheonMail v5.0**, einem AI-gestützten E-Mail-Assistenten mit modularer Architektur und integrierter RAG-Wissensbasis.

> **Hinweis:** Dies ist die **Open-Source Edition (Fiat Lean Mode)** mit optimierter Performance für Standard-Hardware. Für Enterprise-Features (Multi-Lane Consensus, Knowledge Graph, Mission-Based Intelligence) siehe [PantheonRAG Enterprise Core v4.0](../planung/manifest_v4.0.md).

---

## 📋 Schnellzugriff

### Wichtige Dokumente
| Dokument | Beschreibung |
|----------|--------------|
| [README.md](../README.md) | Projektübersicht & Quick Start (Englisch) |
| [readme_tech.md](../readme_tech.md) | Technische Dokumentation (Deutsch) |
| [QUICKSTART.md](QUICKSTART.md) | Installationsanleitung (5 Minuten) |
| [PORTS.md](../PORTS.md) | Port-Konfiguration aller Dienste |

### Kern-Dokumentation
| Dokument | Beschreibung |
|----------|--------------|
| [architecture.md](architecture.md) | Architekturübersicht mit Diagrammen |
| [api-reference.md](api-reference.md) | Vollständige API-Referenz |
| [services.md](services.md) | Service-Architektur und Komponenten |
| [models.md](models.md) | Datenbank-Models und Schema |
| [deployment.md](deployment.md) | Deployment-Guide (Docker & Local) |
| [diagrams.md](diagrams.md) | Visuelle Systemdiagramme |

### Guides & Referenzen
| Dokument | Beschreibung |
|----------|--------------|
| [AUTH_GUIDE.md](AUTH_GUIDE.md) | JWT-Authentifizierung & Login |
| [CHANGELOG.md](CHANGELOG.md) | Versionshistorie & Änderungen |
| [BUGFIX_UI_FLACKERN.md](BUGFIX_UI_FLACKERN.md) | Bug-Report: UI-Flackern behoben |
| [implementation_plan_fiat.md](implementation_plan_fiat.md) | Fiat Lean Strategie |

---

## 🏗️ Architektur-Übersicht

### Hauptkomponenten

```
┌─────────────────────────────────────────────────────────────┐
│              PantheonMail v5.0 (Open-Source)                │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Electron + React + Material-UI)                  │
│           ↕ WebSocket + REST API                            │
│  Backend (FastAPI + SQLAlchemy + Celery)                    │
│           ↕                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Email Client │  │ Draft Service│  │ Learning Mgr │      │
│  │ (IMAP/Gmail) │  │ (AI Drafts)  │  │ (Feedback)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│           ↕                                                 │
│  ┌──────────────────────────────────────────────────┐      │
│  │        Basic RAG Engine (Fiat Lean Mode)         │      │
│  │  • Docling (Document Processing)                 │      │
│  │  • Graph-Lite (SQLite Facts)                     │      │
│  │  • ChromaDB (Vector Database)                    │      │
│  │  • Hybrid Search (Vector + BM25)                 │      │
│  │  • Selective Spock (Semantic Chunking)           │      │
│  └──────────────────────────────────────────────────┘      │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure: SQLite | ChromaDB | Redis | Celery         │
│  LLM Provider: Ollama | OpenAI | Gemini | Anthropic         │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technologie | Version |
|-------|-------------|---------|
| **Frontend** | React | 19.2 |
| **UI Framework** | Material-UI | 5.18 |
| **Desktop** | Electron | 38.2 |
| **Backend** | FastAPI | 0.115 |
| **ORM** | SQLAlchemy | 2.0 |
| **Python** | CPython | 3.11 |
| **Datenbank (Meta)** | SQLite | 3.x |
| **Datenbank (Vektor)** | ChromaDB | 0.5.23 |
| **Cache/Queue** | Redis | 7.x |
| **Worker** | Celery | 5.x |
| **LLM Provider** | Ollama/OpenAI/Gemini/Anthropic | - |
| **Doc Processing** | Docling | latest |
| **Embeddings** | LlamaIndex | latest |

---

## 📖 Dokumentationsbereiche

### 1. Installation & Setup

- [**QUICKSTART.md**](QUICKSTART.md) — Installation in 5 Minuten
  - Voraussetzungen (Docker, Python, Node.js, Ollama)
  - Environment-Konfiguration (.env)
  - Docker-Container starten
  - Frontend bauen und starten
  - Erster Login

- [**deployment.md**](deployment.md) — Detaillierter Deployment-Guide
  - Lokale Entwicklung (Python venv + npm)
  - Docker-basiertes Deployment
  - Modulare Architektur (separate Container)
  - Production-Deployment (mit JWT-Auth)
  - Environment-Variablen Referenz

### 2. Architektur & Design

- [**architecture.md**](architecture.md) — Architektur-Übersicht
  - Modulare Architektur (v5.0+)
  - Komponentendiagramme
  - Datenflussdiagramme
  - Deployment-Architektur
  - MCP-Integration

- [**services.md**](services.md) — Service-Architektur
  - Email Services (IMAP, Gmail, Draft)
  - RAG Services (Ingestion, Query, Collection)
  - Learning Services (Learning Manager, Selective Spock)
  - Infrastructure Services (Health Monitor, Config)
  - Externe Integration (External RAG Connector)

- [**models.md**](models.md) — Datenbank-Models
  - User & Authentication
  - Email & Drafts
  - Learning Pairs
  - RAG Collections & Documents
  - Graph-Lite Facts (SQLite)

- [**diagrams.md**](diagrams.md) — Visuelle Diagramme
  - Architektur-Diagramme (Monolithisch vs. Modular)
  - Datenflussdiagramme (Antwortgenerierung, Lernzyklus)
  - Deployment-Diagramme (Container)
  - Konfigurationsflüsse

### 3. API-Referenz

- [**api-reference.md**](api-reference.md) — Vollständige API-Dokumentation
  - Email Assistant API (Inbox, Drafts, Threads)
  - RAG Module API (Query, Collections, Documents)
  - Authentication API (Login, Register, Refresh)
  - Configuration API (Settings, Services)
  - Dashboard & Analytics API
  - MCP Integration API
  - Fehlercodes & Behandlung

### 4. Authentifizierung & Security

- [**AUTH_GUIDE.md**](AUTH_GUIDE.md) — JWT-Authentifizierung
  - Architektur (Access/Refresh Token)
  - API-Endpunkte (Login, Register, Refresh, Me)
  - Token-Verwaltung im Frontend
  - Auto-Refresh Interceptor
  - Development Mode (DEV_MODE)
  - Security Best Practices
  - Troubleshooting

### 5. Features & Guides

#### Email Management
- Inbox abrufen und filtern
- Thread-Historie anzeigen
- Antwortentwürfe generieren (mit RAG)
- Entwürfe speichern und verwalten
- Auto-Draft Monitoring

#### RAG-Wissensbasis
- Dokumente hochladen (PDF, DOCX, XLSX, TXT)
- Document Ingestion mit Docling
- Collections verwalten
- Hybrid-Suche (Vektor + BM25)
- Selective Spock (Semantisches Chunking)
- Graph-Lite Facts (Entity-Relations)

#### Learning System
- Learning Pairs (Korrektur-Feedback)
- Selective Spock Chunking
- Verbesserte zukünftige Antworten

#### Analytics & Monitoring
- Dashboard-Statistiken
- System-Health-Monitor
- LLM-Usage-Tracking
- API-Call-Statistics

### 6. Enterprise Core v4.0

Für Enterprise-Features siehe die vollständige Dokumentation:

| Dokument | Beschreibung |
|----------|--------------|
| [manifest_v4.0.md](../planung/manifest_v4.0.md) | Enterprise Core Hauptübersicht |
| [manifest_pipeline_v4.0.md](../planung/manifest_pipeline_v4.0.md) | Document Processing Pipeline |
| [manifest_knowledge_v4.0.md](../planung/manifest_knowledge_v4.0.md) | RAG Engine & Knowledge Graph |
| [manifest_quality_v4.0.md](../planung/manifest_quality_v4.0.md) | Six Sigma Quality Assurance |
| [manifest_infrastructure_v4.0.md](../planung/manifest_infrastructure_v4.0.md) | Deployment & Infrastructure |

**Enterprise vs. Open-Source Vergleich:**

| Feature | Open-Source (Fiat) | Enterprise Core v4.0 |
|---------|-------------------|---------------------|
| **RAG Engine** | Basic (ChromaDB, Vector) | Multi-Lane Consensus + Knowledge Graph |
| **Document Processing** | Docling (Single-Lane) | Parallel AI Agents (OCR, Structure, Vision, Legal, Math) |
| **Quality Assurance** | Basic Validation | Six Sigma Refinery + HITL Verification |
| **Intelligence** | Static Configuration | Mission-Based Intelligence |
| **Database** | SQLite + ChromaDB | PostgreSQL + Neo4j + ChromaDB + Redis |
| **Multi-Tenancy** | ❌ Single-User | ✅ Mission Cartridges (RBAC) |

---

## ⚙️ Konfiguration

### Wichtige Environment-Variablen

```bash
# Development Mode (JWT-Auth deaktiviert)
DEV_MODE=true

# JWT Secret (PFLICHT für Production)
JWT_SECRET_KEY=<generieren_mit_openssl_rand_-hex_32>

# LLM Provider (ollama, openai, gemini, anthropic)
LLM_PROVIDER=ollama
LLM_MODEL=llama3:latest

# Email-Konfiguration
EMAIL_PROVIDER=imap
EMAIL_USER=you@example.com
EMAIL_PASSWORD=your-app-password
IMAP_HOST=imap.example.com
IMAP_PORT=993

# Fiat Lean Mode (Performance-Optimierung)
MAIL_EDITION_LEAN=true
EDITION=team

# Infrastruktur
CHROMA_HOST=http://chromadb:8000
REDIS_HOST=redis
REDIS_PORT=6379
OLLAMA_HOST=http://ollama:11434
```

Siehe [.env.example](../.env.example) für alle Optionen.

---

## 🚀 Quick Start

### 1. Repository klonen
```bash
git clone https://github.com/YOUR_USERNAME/mail_modul_fiat.git
cd mail_modul_fiat
```

### 2. Environment konfigurieren
```bash
cp .env.example .env
# .env bearbeiten: EMAIL_USER, EMAIL_PASSWORD, LLM_PROVIDER setzen
```

### 3. Ollama Models pullen
```bash
ollama pull llama3:latest
ollama pull nomic-embed-text:latest
```

### 4. Docker-Container starten
```bash
docker-compose -f docker-compose-modular.yml up --build
```

### 5. Frontend starten
```bash
cd frontend && npm install && npm start
```

### 6. Zugriff

| Service | URL |
|---------|-----|
| **Frontend (Electron)** | Öffnet sich automatisch |
| **Backend API** | http://localhost:33800 |
| **API-Dokumentation** | http://localhost:33800/docs |
| **Health Check** | http://localhost:33800/api/health |

---

## 📊 Ports & Netzwerke

PantheonMail verwendet **konfliktfreie Ports**:

| Service | Port | Protokoll |
|---------|------|-----------|
| Backend API | **33800** | HTTP |
| ChromaDB | **38000** | HTTP |
| Redis | **36379** | TCP |
| Ollama | **11434** | HTTP |

Siehe [PORTS.md](../PORTS.md) für Details.

---

## 🤝 Contributing

Wir freuen uns über Beiträge! Bitte beachte:

- [CONTRIBUTING.md](../CONTRIBUTING.md) — Richtlinien für Beiträge
- [AI_RULES.md](../AI_RULES.md) — Regeln für AI-Agenten

### Entwicklung starten

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 33800

# Frontend (separates Terminal)
cd frontend
npm install
npm start
```

### Tests ausführen

```bash
cd backend
source venv/bin/activate
pytest tests/
```

---

## 📄 Lizenz

Dieses Projekt ist unter der **AGPL-3.0 Lizenz** lizenziert. Siehe [LICENSE](../LICENSE) für Details.

---

## 🙋 Support

### Issues melden
- [GitHub Issues](https://github.com/YOUR_USERNAME/mail_modul_fiat/issues) — Bug-Reports & Feature-Wünsche

### Diskussionen
- [GitHub Discussions](https://github.com/YOUR_USERNAME/mail_modul_fiat/discussions) — Allgemeine Fragen

### Dokumentation
- [readme_tech.md](../readme_tech.md) — Technische Dokumentation
- [planung/manifest_v4.0.md](../planung/manifest_v4.0.md) — Enterprise Core v4.0

---

## 📈 Status

| Service | Status | Version |
|---------|--------|---------|
| **Backend API** | ✅ Stabil | v5.0.0 |
| **Frontend** | ✅ Stabil | v5.0.0 |
| **RAG Engine (Basic)** | ✅ Stabil | v5.0.0 |
| **Email Integration** | ✅ Stabil (IMAP) | v5.0.0 |
| **Learning System** | ✅ Stabil | v5.0.0 |
| **Analytics** | ✅ Stabil | v5.0.0 |
| **JWT Authentication** | ✅ Stabil | v5.0.0 |

---

**PantheonMail v5.0** — Dein intelligenter E-Mail-Assistent mit integrierter Wissensbasis.

**Enterprise?** Siehe [PantheonRAG Enterprise Core v4.0](../planung/manifest_v4.0.md) für Multi-Lane Consensus, Knowledge Graph und Mission-Based Intelligence.
