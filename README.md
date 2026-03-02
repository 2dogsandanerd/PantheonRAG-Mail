# 📧 PantheonRAG-Mail v1.0

**Open-Source AI Email Assistant with Integrated Knowledge Base**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker--compose-ready-blue.svg)](https://docs.docker.com/compose/)

> **💡 Note:** This is the **Open-Source Edition** with basic RAG functionality. For enterprise features (Multi-Lane Consensus, Knowledge Graph, Mission-Based Intelligence) see [PantheonRAG Enterprise Core v4.0](planung/manifest_v4.0.md).

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Ollama (optional, for local LLMs)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/mail_modul_fiat.git
cd mail_modul_fiat

# 2. Configure environment
cp .env.example .env
# Edit .env: Set EMAIL_USER, EMAIL_PASSWORD, LLM_PROVIDER

# 3. Start Docker containers
docker-compose up --build

# 4. Start frontend
cd frontend && npm install && npm start
```

### Access After Startup

| Service | URL |
|---------|-----|
| **Frontend (Electron)** | Opens automatically |
| **Backend API** | http://localhost:33800 |
| **API Documentation** | http://localhost:33800/docs |
| **Health Check** | http://localhost:33800/api/health |

---

## ✨ Features

### 🤖 AI-Powered Email Drafts
- **Context-sensitive responses** based on your documented knowledge
- **Multi-Provider LLM Support**: Ollama (local), OpenAI, Gemini, Anthropic
- **Learning system**: Automatically improves through your feedback

### 📚 Integrated Knowledge Base (Basic RAG)
- **Document Ingestion**: PDF, DOCX, XLSX, TXT, Markdown
- **Vector Search**: ChromaDB with Hybrid Search (Vector + BM25)
- **Smart Chunking**: Automatic segmentation for optimal matches
- **Source Tracking**: Every answer shows its origin

### 📧 Email Management
- **Multi-Protocol**: IMAP (all providers) + Gmail OAuth2
- **Smart Drafts**: AI-generated drafts with context
- **Thread History**: Complete conversation overview
- **Learning Pairs**: System learns from your corrections

### 📊 Analytics Dashboard
- **Real-time metrics**: Email volume, response times, activity
- **System Health**: Status of all services (Ollama, ChromaDB, Redis)
- **LLM Usage**: Token consumption, cost tracking
- **Internationalization**: German & English

---

## 🏗️ Architecture

### This Edition (PantheonRAG-Mail v1.0)

```
┌─────────────────────────────────────────────────────────────┐
│              PantheonRAG-Mail (Open-Source)                 │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Electron + React + MUI)                          │
│           ↕ WebSocket + REST API                            │
│  Backend (FastAPI + SQLAlchemy)                             │
│           ↕                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Email Client │  │ Draft Service│  │ Learning Mgr │      │
│  │ (IMAP/Gmail) │  │ (AI Drafts)  │  │ (Feedback)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│           ↕                                                 │
│  ┌──────────────────────────────────────────────────┐      │
│  │        Basic RAG Engine                          │      │
│  │  • Docling (Document Processing)                 │      │
│  │  • ChromaDB (Vector Database)                    │      │
│  │  • Hybrid Search (Vector + BM25)                 │      │
│  └──────────────────────────────────────────────────┘      │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure: SQLite | ChromaDB | Redis | Celery         │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 19.2, Material-UI 5.18, Electron 38.2 |
| **Backend** | FastAPI 0.115, SQLAlchemy 2.0, Python 3.11 |
| **Database** | SQLite (metadata), ChromaDB (vectors) |
| **Worker** | Celery + Redis (async tasks) |
| **LLM Provider** | Ollama, OpenAI, Gemini, Anthropic |
| **Document Processing** | Docling, LlamaIndex |

---

## 🚀 Enterprise Core v4.0 – The Big Brother

**PantheonRAG-Mail** is the **open-source addon** for email integration with basic RAG.

For **enterprise requirements**, there's **PantheonRAG Enterprise Core v4.0** with:

### Enterprise Features (not in this edition)

| Feature | PantheonRAG-Mail (Open-Source) | Enterprise Core v4.0 |
|---------|-------------------------------|---------------------|
| **RAG Engine** | Basic (ChromaDB, Vector) | Multi-Lane Consensus + Knowledge Graph |
| **Document Processing** | Docling (Single-Lane) | Parallel AI Agents (OCR, Structure, Vision, Legal, Math) |
| **Quality Assurance** | Basic Validation | Six Sigma Refinery + HITL Verification |
| **Observability** | Basic Health Check | Glasshouse (Full Observability Stack) |
| **Intelligence** | Static Configuration | Mission-Based Intelligence (Adaptive Routing) |
| **Database** | SQLite + ChromaDB | PostgreSQL + Neo4j + ChromaDB + Redis |
| **Multi-Tenancy** | ❌ Single-User | ✅ Mission Cartridges (RBAC, Isolation) |
| **Accuracy** | ~85-90% | 93.61% Auto + 100% Post-HITL |

### Enterprise Core Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│         PantheonRAG Enterprise Core v4.0                         │
├──────────────────────────────────────────────────────────────────┤
│  Mission Control (Adaptive Intelligence)                         │
│           ↕                                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  The Pipeline (Multi-Lane Consensus)                    │    │
│  │  Enhanced Janus → Solomon Consensus → HITL Verification │    │
│  │  Lanes: OCR | Structure | Vision | Legal | Math         │    │
│  └─────────────────────────────────────────────────────────┘    │
│           ↕                                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  The Brain (Hybrid Intelligence)                        │    │
│  │  Spock (Vector) + Mercator (Graph) + Agent (Fusion)     │    │
│  │  Neo4j Knowledge Graph + ChromaDB Vectors               │    │
│  └─────────────────────────────────────────────────────────┘    │
│           ↕                                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  The Guardians (Quality Assurance)                      │    │
│  │  Glasshouse (Observability) + Laboratory (Six Sigma)    │    │
│  └─────────────────────────────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────────┤
│  Infrastructure: PostgreSQL | Neo4j | ChromaDB | Redis | MinIO  │
└──────────────────────────────────────────────────────────────────┘
```

### Enterprise Core Documentation

Full Enterprise Core v4.0 documentation is located at:
- 📄 [`planung/manifest_v4.0.md`](planung/manifest_v4.0.md) — Main manifest
- 📄 [`planung/manifest_pipeline_v4.0.md`](planung/manifest_pipeline_v4.0.md) — Pipeline
- 📄 [`planung/manifest_knowledge_v4.0.md`](planung/manifest_knowledge_v4.0.md) — Knowledge
- 📄 [`planung/manifest_quality_v4.0.md`](planung/manifest_quality_v4.0.md) — Quality
- 📄 [`planung/manifest_infrastructure_v4.0.md`](planung/manifest_infrastructure_v4.0.md) — Infrastructure

### Upgrade Path

**From PantheonRAG-Mail to Enterprise Core:**

1. **Start with PantheonRAG-Mail** (this repo)
   - Learn the basics
   - Test email integration
   - Understand RAG fundamentals

2. **Upgrade to Enterprise Core** (separate repo)
   - Multi-Lane Consensus Pipeline
   - Knowledge Graph (Neo4j)
   - Mission-Based Intelligence
   - Six Sigma Quality Assurance

3. **Integration**
   - PantheonRAG-Mail can serve as **email addon** for Enterprise Core
   - Enterprise Core provides RAG API to PantheonRAG-Mail
   - Shared knowledge base possible

---

## ⚙️ Configuration

### Important Environment Variables (.env)

```bash
# LLM Provider (ollama, openai, gemini, anthropic)
LLM_PROVIDER=ollama
LLM_MODEL=llama3:latest

# Email Configuration
EMAIL_PROVIDER=imap
EMAIL_USER=your@email.com
EMAIL_PASSWORD=your-app-password
IMAP_HOST=imap.email.com
IMAP_PORT=993

# Development (JWT auth disabled for faster dev)
DEV_MODE=true

# Fiat Lean Mode (Performance Optimization)
MAIL_EDITION_LEAN=true
EDITION=team
```

### Configure LLM Provider

**Ollama (local, free):**
```bash
# Install Ollama: https://ollama.ai
ollama pull llama3:latest
ollama pull nomic-embed-text:latest
```

**OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

**Google Gemini:**
```bash
LLM_PROVIDER=gemini
GOOGLE_API_KEY=AIza...
```

---

## 📖 Documentation

### Main Documentation
- [`readme_v4.md`](readme_v4.md) — Technical documentation (this repo)
- [`PORTS.md`](PORTS.md) — Port configuration of all services
- [`docs/`](docs/) — Additional documentation

### Enterprise Core v4.0
- [`planung/manifest_v4.0.md`](planung/manifest_v4.0.md) — Enterprise Core Manifest
- [`planung/manifest_pipeline_v4.0.md`](planung/manifest_pipeline_v4.0.md) — Pipeline
- [`planung/manifest_knowledge_v4.0.md`](planung/manifest_knowledge_v4.0.md) — Knowledge
- [`planung/manifest_quality_v4.0.md`](planung/manifest_quality_v4.0.md) — Quality
- [`planung/manifest_infrastructure_v4.0.md`](planung/manifest_infrastructure_v4.0.md) — Infrastructure

### API Documentation
Available after startup at: http://localhost:33800/docs

### Quick Guides
- **Getting Started:** See Quick Start above
- **Email Setup:** Configure `.env` with IMAP credentials
- **Upload Documents:** RAG Management tab in frontend
- **Generate Drafts:** Inbox → Select email → "Generate Draft"

---

## 🗺️ Roadmap

### v1.0 (Current Release)
- ✅ AI-powered email drafts
- ✅ Integrated knowledge base (Basic RAG)
- ✅ Multi-Provider LLM Support
- ✅ Learning System
- ✅ Analytics Dashboard

### v2.0 (In Development)
- 🔲 App Authentication (JWT, Multi-User)
- 🔲 Rate Limiting for Production
- 🔲 Auto-Draft Monitoring (Background Processing)
- 🔲 API Call Tracking & Statistics
- 🔲 Setup Wizard (Guided Initial Configuration)

### v3.0 (Planned)
- 🔲 Enterprise Integration (PantheonRAG Core v4.0 API)
- 🔲 Mail-Module Entanglement (External RAG Module)
- 🔲 Code Signing & Auto-Update
- 🔲 Glasshouse Integration (Observability)

---

## 🤝 Contributing

We welcome contributions! Please read first:

- [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution guidelines
- [AI_RULES.md](AI_RULES.md) — Rules for AI agents

### Start Development

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 33800

# Frontend (separate terminal)
cd frontend
npm install
npm start
```

### Run Tests

```bash
cd backend
source venv/bin/activate
pytest test/
```

---

## 📄 License

This project is licensed under the **AGPL-3.0 License**. See [LICENSE](LICENSE) for details.

---

## 🙋 Support

### Report Issues
- [GitHub Issues](https://github.com/YOUR_USERNAME/mail_modul_fiat/issues) — Bug Reports & Feature Requests

### Questions & Discussions
- [GitHub Discussions](https://github.com/YOUR_USERNAME/mail_modul_fiat/discussions) — General questions

### Documentation
- [readme_v4.md](readme_v4.md) — Technical documentation (this repo)
- [planung/manifest_v4.0.md](planung/manifest_v4.0.md) — Enterprise Core v4.0

---

## 📊 Status

| Service | Status |
|---------|--------|
| **Backend API** | ✅ Stable |
| **Frontend** | ✅ Stable |
| **RAG Engine (Basic)** | ✅ Stable |
| **Email Integration** | ✅ Stable (IMAP) |
| **Learning System** | ✅ Stable |
| **Analytics** | ✅ Stable |

---

**PantheonRAG-Mail** — Your intelligent email assistant with integrated knowledge.

**Enterprise?** See [PantheonRAG Enterprise Core v4.0](planung/manifest_v4.0.md) for Multi-Lane Consensus, Knowledge Graph and Mission-Based Intelligence.
