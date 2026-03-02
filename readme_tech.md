# 📧 PantheonRAG-Mail v1.0 — Technische Dokumentation

> **Hinweis:** Dies ist die **Open-Source Edition**. Für Enterprise-Features siehe [PantheonRAG Enterprise Core v4.0](planung/manifest_v4.0.md).

## 🚀 Übersicht
PantheonRAG-Mail ist ein hochmoderner, AI-gestützter Email-Assistent für den Enterprise-Einsatz. Die Anwendung kombiniert die Flexibilität einer Electron-Desktop-App mit der Power eines FastAPI/LlamaIndex RAG-Backends.

---

> [!NOTE]
> **Fiat Strategie (Lean Mode)**: Diese Edition ist als "Surgical Cut" optimiert für maximale Geschwindigkeit auf Standard-Hardware. Schwere Enterprise-Komponenten (Neo4j, Multi-Lane RAG) wurden durch effiziente Alternativen wie **Graph-Lite** und **Selective Spock** ersetzt.

> [!TIP]
> **Development Mode:** `DEV_MODE=true` deaktiviert JWT-Auth für schnelle lokale Entwicklung.

---

## ✨ Features
- **Multi-Provider LLM Support:** Nahtlose Integration von Ollama (lokal), OpenAI, Gemini und Anthropic.
- **Advanced RAG System:**
    - **Lean Extraction (Fiat Tuning):** Priorisierung von `Docling` (Goethe Lane) für digitale Dokumente; Multi-Lane "Refinery" nur bei niedriger Konfidenz.
    - **Selective Spock:** Semantisches Chunking exklusiv für "Learning Pairs" zur Qualitätssteigerung ohne Performance-Einbußen.
    - **Graph-Lite Integration:** Entity-Relation Facts via SQLite statt Neo4j zur Reduktion des Ressourcenverbrauchs.
    - Hybrid-Suche (Vektor-Ähnlichkeit + BM25 Keyword-Suche).
    - Domänen-basiertes Routing für gezielte Abfragen.

### 📧 Email Management
- **Multi-Protokoll:** Unterstützung für Gmail (OAuth2) und klassisches IMAP.
- **Smart Drafting:** Kontextsensitive Antwortentwürfe basierend auf dem RAG-Wissen
- **Learning System:** Das System lernt aus manuellen Korrekturen des Nutzers und verbessert zukünftige Entwürfe.

### 📊 Analytics & Monitoring
- **Analytics Dashboard:** Echtzeit-Visualisierung von Engagement-Scores und Aktivitätsmetriken.
- **System Health Monitor:** Automatisierte Überwachung der Dienste (Ollama, ChromaDB).
- **Internationalisierung (i18n):** Voller Support für Deutsch und Englisch.

---

## 📖 Kurz-Dokumentation

### Architektur
- **Frontend:** React 19.2 + Material-UI 5.18 in einer Electron 38.2 Umgebung.
- **Backend:** FastAPI 0.115 mit SQLAlchemy 2.0.
- **Database:** SQLite für Metadaten, Learning & **Graph-Lite Facts**; ChromaDB (Vektor-Datenbank) für das RAG-Wissen.
- **Worker:** Celery + Redis für asynchrone Ingestion- und Monitoring-Tasks.

### Konfiguration
- **MAIL_EDITION_LEAN=true**: Aktiviert alle "Fiat-Tuning" Optimierungen (Default).

### RAG-Workflow
1. **Ingestion:** Dokumente werden via Docling analysiert, segmentiert und in ChromaDB indiziert.
2. **Query:** Bei einer eingehenden Mail sucht der `QueryService` via Hybrid-Suche nach relevantem Kontext.
3. **Generation:** Das LLM erhält den Kontext + System-Prompt und generiert einen Entwurf im `DraftService`.

### Installation (Quick Start)
1. `python3 -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. `cd frontend && npm install`
4. `npm start` (startet UI + Backend automatisch)

### ⚠️ Ports
**mail_modul_fiat verwendet konfliktfreie Ports:**
- Backend: **33800**
- ChromaDB: **38000** (nicht 8000!)
- Redis: **36379** (nicht 6379!)
- Ollama: **11434** (geteilt mit ClawRAG)

Siehe [PORTS.md](PORTS.md) für Details.

---

## 🗺️ Roadmap v5.1 (Offene Punkte & Features)

### 💎 1. The Refinery Path (Glasshouse Integration)
- **Phase 1: API-Anbindung (2-3 Wochen)**
    - [ ] `ExtractionService`: Integration des Glasshouse `ingest-service` (:42001) als Multi-Lane Upgrade.
    - [ ] `DraftService`: Orchestrierung via Glasshouse `agent-service` (:42003) für Graph+Vector-Fusion.
- **Phase 2: Verified Draft Feature (1-2 Wochen)**
    - [ ] **"Verify & Draft" Button:** Implementierung einer Surgical HITL-Ansicht für kritische Fakten.
    - [ ] **Provenance-Highlighting:** Direkte Verlinkung von Draft-Zahlen auf die Original-PDF-Ausschnitte.
- **Phase 3: Enterprise Audit & RBAC**
    - [ ] **Trust Analytics:** Integration des Glasshouse Audit Trails in das Dashboard.
    - [ ] **Spectral Lenses:** Einbindung von Performance- und Security-Lenses in den Health Monitor.

### 🔐 2. Enterprise Security & Multi-Tenancy (v5.0 ABGESCHLOSSEN)
- [x] **JWT Authentication:** Vollständige Implementierung mit Access/Refresh Token Rotation
- [x] **Login UI:** React-basierte Login/Register-Komponente mit Auto-Refresh
- [x] **Development Mode:** `DEV_MODE` Switch für Auth-Deaktivierung im Development
- [ ] **Tenant Isolation:** Saubere Trennung von Daten und Collections pro Mandant.
- [ ] **RBAC (Role-Based Access Control):** Granulare Berechtigungen (Admin, User, Read-only).

### ⚡ 3. Performance & Fiat Tuning
- [ ] **Advanced Caching:** Implementierung eines Redis-basierten Embedding- und Query-Caches.
- [ ] **Local LLM Presets:** Optimierte Profile für Qwen2-7B und Mistral-v0.3.

### 🎨 4. UX & Distribution
- [x] **Setup Wizard:** Onboarding-Wizard integriert (v5.0)
- [ ] **Code Signing:** Signierte Binarys für Windows und macOS Distribution.
- [ ] **Auto-Update:** Integrierter Mechanismus für nahtlose Anwendungs-Updates.

### 📊 5. Statistics & Analytics Enhancement
- [ ] **Improved Statistics:** Detaillierte Tracking- und Statistikfunktionen für API-Aufrufe und Query-Performance in der Datenbank.

---

## 🛠️ Entwicklung (v5.0 Updates)

### Environment Variablen

| Variable | Standard | Beschreibung |
|----------|----------|--------------|
| `DEV_MODE` | `false` | Wenn `true`: JWT-Auth deaktiviert (nur für Development!) |
| `JWT_SECRET_KEY` | - | **PFLICHT für Production** - Generieren mit `openssl rand -hex 32` |
| `MAIL_EDITION_LEAN` | `true` | Aktiviert Fiat-Tuning Optimierungen |
| `EDITION` | `team` | Feature-Edition (developer/team/enterprise) |
| `EXTERNAL_RAG_ENABLED` | `false` | Externes RAG-Modul verwenden |
| `LLM_PROVIDER` | `ollama` | LLM-Provider (ollama/openai/gemini/anthropic) |

### Quick Start für Development

```bash
# 1. Repository klonen
git clone https://github.com/YOUR_ORG/pantheonmail.git
cd pantheonmail

# 2. Environment kopieren und DEV_MODE aktivieren
cp .env.example .env
# In .env setzen: DEV_MODE=true

# 3. Ollama Models pullen
ollama pull llama3:latest
ollama pull nomic-embed-text:latest

# 4. Docker-Container starten
docker-compose -f docker-compose-modular.yml up --build

# 5. Frontend starten
cd frontend && npm install && npm start
```

**Hinweis:** Mit `DEV_MODE=true` wird kein Login benötigt – die App öffnet sich direkt.

### Production Deployment

```bash
# 1. JWT_SECRET_KEY generieren
openssl rand -hex 32

# 2. In .env eintragen:
JWT_SECRET_KEY=<dein_geheimer_schluessel>
DEV_MODE=false

# 3. Docker-Container starten
docker-compose -f docker-compose-modular.yml up -d

# 4. Ersten Admin-User anlegen (via API)
curl -X POST http://localhost:33800/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"sicheres_passwort"}'
```
