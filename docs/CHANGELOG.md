# Changelog

Alle wesentlichen Änderungen an PantheonRAG-Mail.

> **Hinweis:** Dies ist die **Open-Source Edition**. Für Enterprise-Features siehe [PantheonRAG Enterprise Core v4.0](../planung/manifest_v4.0.md).

---

## [5.0.0] - 2026-03-01

### ✨ Hinzugefügt

#### 🔐 Authentication System (VOLLSTÄNDIG)
- **JWT-basierte Authentifizierung** mit Access/Refresh Token Rotation
  - `backend/src/core/auth.py`: Vollständige Auth-Implementierung
  - `backend/src/api/v1/deps.py`: JWT Dependency Injection
  - `backend/src/api/v1/auth.py`: Login/Register/Refresh/Me Endpoints
- **Development Mode** (`DEV_MODE=true`)
  - Deaktiviert JWT-Auth für schnelle lokale Entwicklung
  - Dummy-User wird automatisch verwendet
  - Einfache Umschaltung für Production via Umgebungsvariable
- **Frontend Login UI**
  - `frontend/src/components/LoginForm.jsx`: Login/Register-Komponente
  - `frontend/src/App.jsx`: Auth-Gate mit Loading-State
  - `frontend/src/api/auth.js`: Token-Management mit Auto-Refresh
  - Automatischer Token-Refresh bei 401-Fehlern
  - Secure Logout mit Token-Löschung

#### 🐛 Bug Fixes
- **Endlos-Reload behoben**: `window.location.reload()` im Auth-Interceptor entfernt
  - Verhindert Auth-Loop beim Start mit ungültigem Token
  - App zeigt jetzt sauber Login-Formular statt Reload-Schleife
- **Celery Worker Shutdown**: Saubere Handler für `will-quit` Event
- **Auth-Check Race Condition**: `useEffect` mit leerem Dependency-Array

#### 📝 Dokumentation
- **README v5.0**: Vollständige Überarbeitung mit Auth-Features
- **Environment Variablen**: `DEV_MODE` in `.env.example` dokumentiert
- **Quickstart Guides**: Development vs. Production Pfade klar getrennt

### 🔧 Geändert

#### Backend
- `backend/src/api/v1/dependencies.py`:
  - `get_current_user` jetzt conditional via `DEV_MODE`
  - Development: Dummy-User ohne JWT
  - Production: Echte JWT-Validierung via `src.core.auth`
- **Alle Router-Dateien** auf `CurrentUser` Dependency umgestellt:
  - `email.py`, `rag.py`, `learning.py`, `statistics.py`
  - `analytics.py`, `auto_draft.py`, `dashboard.py`, `evaluation.py`
  - `tasks.py`, `config.py`, `docs.py`, `services.py`

#### Frontend
- `frontend/src/api/auth.js`:
  - Kein `window.location.reload()` mehr im Error-Handler
  - Graceful Degradation bei Token-Fehlern
- `frontend/src/App.jsx`:
  - Auth-State mit Loading-Indicator
  - Login-Form wird vor Haupt-UI gerendert
  - Logout-Button im Header

#### Configuration
- `.env.example`: `DEV_MODE=false` als Standard
- `.env.modular`: `DEV_MODE=true` für Development
- `docker-compose-modular.yml`: `.env` wird in Container gemounted

### 📦 Technische Details

#### Auth-Flow (Production)
```
1. User öffnet App → authLoading=true
2. checkAuth() ruft /auth/me mit gespeichertem Token
3a. Token gültig → isAuthenticated=true → Haupt-UI
3b. Token ungültig/401 → isAuthenticated=false → Login-Form
4. Login → /auth/login → Access+Refresh Token
5. Token in localStorage + Auto-Interceptor für alle Requests
6. Bei 401: Auto-Refresh via /auth/refresh
7. Bei Refresh-Fehler: Logout + Login-Form
```

#### Development Mode
```
DEV_MODE=true → get_current_user() returns dummy user
- username: "dev_user"
- email: "dev@localhost"
- role: "admin"
- Kein JWT erforderlich
- Alle Endpoints sofort verfügbar
```

### ⚠️ Breaking Changes

#### Für bestehende Installationen
- **JWT_SECRET_KEY erforderlich**: Production-Deployments MÜSSEN `JWT_SECRET_KEY` setzen
- **Alle API-Clients benötigen Auth**: Geschützte Endpoints geben 401 ohne Token
- **Token-Storage**: Frontend speichert Tokens in localStorage (`pantheonmail_token`)

#### Migration
```bash
# 1. JWT_SECRET_KEY generieren
openssl rand -hex 32

# 2. In .env eintragen
JWT_SECRET_KEY=<generated_key>
DEV_MODE=false

# 3. Backend neu starten
docker-compose restart email_assistant

# 4. Ersten User anlegen
curl -X POST http://localhost:33800/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"secure_password"}'
```

---

## [4.0.0] - 2026-02-20

### ✨ Hinzugefügt
- **Fiat Lean Mode**: Optimierte RAG-Pipeline mit Docling
- **Graph-Lite**: SQLite-basierte Entity-Relations statt Neo4j
- **Selective Spock**: Semantisches Chunking für Learning Pairs
- **Multi-Provider LLM**: Ollama, OpenAI, Gemini, Anthropic
- **Celery Worker**: Asynchrone Task-Verarbeitung mit Redis

### 🔧 Geändert
- **Port-Konfiguration**: Konfliktfreie Ports (33800, 38000, 36379)
- **Modulare Architektur**: RAG-Modul separat hostbar

---

## Versionskonvention

- **MAJOR.MINOR.PATCH** (SemVer)
- **MAJOR**: Breaking Changes
- **MINOR**: Neue Features (abwärtskompatibel)
- **PATCH**: Bug Fixes (abwärtskompatibel)

---

## upcoming v5.1 (Geplant)

### In Arbeit
- [ ] Tenant Isolation für Multi-User-Betrieb
- [ ] RBAC (Role-Based Access Control)
- [ ] Advanced Caching mit Redis
- [ ] Code Signing für Distribution

### Überlegt
- [ ] WebSocket-basierte Realtime-Updates
- [ ] Offline-Mode mit lokaler Sync
- [ ] Mobile App (React Native)
