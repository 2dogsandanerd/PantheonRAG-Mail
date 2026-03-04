# PantheonMail — Quickstart Guide

**In 5 Minuten zum ersten AI-Draft**

---

## Voraussetzungen

| Tool | Version | Install |
|------|---------|---------|
| **Docker** | 24+ | [docker.com/get-docker](https://docs.docker.com/get-docker/) |
| **Docker Compose** | 2.20+ | In Docker Desktop enthalten |
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 20+ | [nodejs.org](https://nodejs.org/) |
| **Ollama** (optional) | latest | [ollama.ai](https://ollama.ai) |

> **Kein Ollama?** Du kannst auch OpenAI, Gemini oder Anthropic verwenden — setze `LLM_PROVIDER` entsprechend in `.env`.

---

## Schritt 1: Repository klonen

```bash
git clone https://github.com/YOUR_USERNAME/mail_modul_fiat.git
cd mail_modul_fiat
```

---

## Schritt 2: Environment konfigurieren

```bash
cp .env.example .env
```

Öffne `.env` in deinem Editor und setze **mindestens**:

```bash
# === DEVELOPMENT MODE ===
# true = Kein Login erforderlich (schneller für Development)
DEV_MODE=true

# === JWT Secret (PFLICHT für Production!) ===
# Generieren mit: openssl rand -hex 32
JWT_SECRET_KEY=CHANGE_ME_generate_with_openssl_rand_-hex_32

# === LLM Provider ===
LLM_PROVIDER=ollama
LLM_MODEL=llama3:latest

# === Email-Konfiguration ===
EMAIL_USER=you@example.com
EMAIL_PASSWORD=your-app-password-not-login-password
IMAP_HOST=imap.example.com
IMAP_PORT=993

# === Fiat Lean Mode (Performance) ===
MAIL_EDITION_LEAN=true
EDITION=team
```

### Email-Passwort (WICHTIG!)

**Gmail:** Verwende ein [App-Passwort](https://support.google.com/accounts/answer/185833), nicht dein normales Passwort.

**Office 365:** Verwende `outlook.office365.com` als IMAP-Host.

**Andere Provider:** App-spezifisches Passwort erforderlich.

---

## Schritt 3: Ollama Models pullen

```bash
# Sprachmodell (für Draft-Generierung)
ollama pull llama3:latest

# Embedding-Modell (für RAG-Suche)
ollama pull nomic-embed-text:latest
```

> **Dauer:** Ca. 5-10 Minuten (abhängig von der Internetverbindung)

---

## Schritt 4: Docker-Container starten

```bash
# Modulare Architektur (empfohlen)
docker-compose -f docker-compose-modular.yml up --build
```

**Erster Start:** 2-5 Minuten (baut Images, initialisiert Datenbanken)

### Log-Ausgabe beobachten

```bash
# In einem zweiten Terminal
docker-compose logs -f
```

**Erfolgreicher Start:**
```
✓ PantheonMail API running on http://localhost:33800
✓ ChromaDB connected
✓ Ollama available
✓ Database initialized
```

---

## Schritt 5: Frontend starten

```bash
cd frontend
npm install
npm start
```

**Frontend startet:**
- Electron-App öffnet sich automatisch
- Bei `DEV_MODE=true`: Direkter Zugriff ohne Login
- Bei `DEV_MODE=false`: Login erforderlich

---

## Schritt 6: Erster Zugriff

### Bei DEV_MODE=true (Development)

✅ **Kein Login erforderlich** — App öffnet sich direkt mit allen Features.

### Bei DEV_MODE=false (Production)

1. **API-Dokumentation öffnen:**
   ```
   http://localhost:33800/docs
   ```

2. **Ersten User registrieren:**
   ```bash
   curl -X POST http://localhost:33800/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "email": "admin@example.com",
       "password": "sicheres_passwort_123"
     }'
   ```

3. **Login durchführen:**
   ```bash
   curl -X POST http://localhost:33800/api/v1/auth/login \
     -d "username=admin&password=sicheres_passwort_123"
   ```

4. **Token im Frontend verwenden:**
   - Token aus Login-Response kopieren
   - Im Login-Formular eingeben (falls erforderlich)

---

## Was jetzt?

### 1. Wissensbasis aufbauen

Gehe zum **RAG**-Tab im Frontend und lade deine ersten Dokumente hoch:
- PDFs
- Word-Dokumente (DOCX)
- Excel-Tabellen (XLSX)
- Textdateien (TXT, Markdown)

**Oder via API:**
```bash
curl -X POST http://localhost:33800/api/v1/rag/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "collection_name=my_knowledge_base"
```

### 2. Inbox abrufen

```bash
curl http://localhost:33800/api/v1/email/inbox \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Ersten Draft generieren

```bash
curl -X POST http://localhost:33800/api/v1/email/draft \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "client@example.com",
    "subject": "Question about pricing",
    "body": "Hi, I would like to know more about your enterprise plan.",
    "thread_id": "thread_123",
    "use_rag": true
  }'
```

**Response:**
```json
{
  "draft": "Sehr geehrter Kunde, gerne sende ich Ihnen unsere Enterprise-Preise...",
  "rag_context": "Preisliste 2026: Enterprise ab 99€/Monat...",
  "rag_status": "success"
}
```

---

## Services & URLs

| Service | URL | Status |
|---------|-----|--------|
| **Backend API** | http://localhost:33800 | ✅ |
| **API-Dokumentation** | http://localhost:33800/docs | ✅ |
| **Health Check** | http://localhost:33800/api/health | ✅ |
| **RAG Module** | http://localhost:8080 | ✅ |
| **ChromaDB** | http://localhost:38000 | ✅ |
| **Redis** | localhost:36379 | ✅ |
| **Ollama** | http://localhost:11434 | ✅ |

---

## Troubleshooting

### Backend startet nicht

```bash
# Logs prüfen
docker-compose logs email_assistant

# Häufige Ursachen:
# - JWT_SECRET_KEY nicht gesetzt
# - Datenbank-Pfade haben keine Schreibrechte
# - Port 33800 bereits belegt
```

**Lösung:**
```bash
# Port prüfen
sudo lsof -i :33800

# Berechtigungen setzen
chmod -R 755 ./backend/data
```

---

### Ollama-Verbindung fehlgeschlagen

```bash
# Ollama läuft?
ollama serve

# Models vorhanden?
ollama list

# Sollte zeigen:
# NAME              ID           SIZE
# llama3:latest     ...          ...
# nomic-embed-text  ...          ...
```

**Docker-Host-Problem:**
```bash
# In .env prüfen:
OLLAMA_HOST=http://host.docker.internal:11434

# Linux: host.docker.internal ist nicht verfügbar
# Lösung: Ollama-Container verwenden oder Netzwerk konfigurieren
```

---

### IMAP-Authentifizierung fehlgeschlagen

**Gmail:**
- 2-Faktor-Authentifizierung aktivieren
- App-Passwort erstellen: https://myaccount.google.com/apppasswords
- App-Passwort in `.env` eintragen

**Office 365:**
- Modern Auth erforderlich
- IMAP-Host: `outlook.office365.com`
- Port: `993` (SSL)

---

### ChromaDB-Fehler: "Connection refused"

```bash
# ChromaDB-Logs prüfen
docker-compose logs chromadb

# Volume-Probleme
docker-compose down -v
docker-compose up --build
```

---

### Frontend zeigt weißen Bildschirm

```bash
# Frontend-Cache leeren
rm -rf frontend/.webpack
rm -rf frontend/node_modules/.cache

# Neu bauen
cd frontend
npm install
npm start
```

---

### JWT-Auth-Probleme (DEV_MODE=false)

**Fehler:** "401 Unauthorized bei allen Requests"

**Lösung:**
```bash
# 1. JWT_SECRET_KEY in .env prüfen
# Muss gesetzt sein und darf nicht der Default-Wert sein

# 2. Token generieren
curl -X POST http://localhost:33800/api/v1/auth/login \
  -d "username=admin&password=..."

# 3. Token im Header verwenden
curl -H "Authorization: Bearer <token>" http://localhost:33800/api/v1/email/inbox
```

---

## Modulare Architektur (Advanced)

### RAG-Modul separat betreiben

Nützlich wenn:
- Mehrere Apps dasselbe RAG-Modul teilen
- RAG-Modul auf separatem Server laufen soll

```bash
# 1. RAG-Modul starten
docker-compose -f docker-compose-modular.yml up rag_module rag_chromadb -d

# 2. Email Assistant mit externem RAG starten
# In .env setzen:
EXTERNAL_RAG_ENABLED=true
EXTERNAL_RAG_URL=http://localhost:8080

docker-compose -f docker-compose-modular.yml up email_assistant -d
```

---

## Lokale Entwicklung (ohne Docker)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env prüfen
cp .env.example .env

# Starten
uvicorn src.main:app --reload --port 33800
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### Externe Dienste (Docker)

```bash
# Nur ChromaDB und Redis (ohne Email Assistant)
docker-compose up chromadb redis -d
```

---

## Nächste Schritte

### 1. Onboarding-Wizard

Das Frontend zeigt beim ersten Start einen Setup-Wizard:
- Email-Konfiguration testen
- LLM-Provider konfigurieren
- Erstes Dokument hochladen

### 2. Wissensbasis erweitern

- Mehrere Collections erstellen (z.B. "Produkte", "Preise", "FAQ")
- Dokumente kategorisieren
- Learning Pairs sammeln (Korrekturen speichern)

### 3. Auto-Draft aktivieren

```bash
# Hintergrund-Prozess für automatische Draft-Generierung
curl -X POST http://localhost:33800/api/v1/auto-draft/start
```

### 4. Dashboard & Analytics

- E-Mail-Statistiken anzeigen
- LLM-Nutzung tracken
- System-Health überwachen

---

## Hilfe & Support

### Dokumentation

- [index.md](docs/index.md) — Hauptübersicht
- [architecture.md](docs/architecture.md) — Architektur
- [api-reference.md](docs/api-reference.md) — API-Referenz
- [AUTH_GUIDE.md](docs/AUTH_GUIDE.md) — Authentifizierung

### Issues

- [GitHub Issues](https://github.com/YOUR_USERNAME/mail_modul_fiat/issues)

### Community

- [GitHub Discussions](https://github.com/YOUR_USERNAME/mail_modul_fiat/discussions)

---

**Viel Erfolg mit PantheonMail! 🚀**

Bei Fragen oder Problemen: Einfach ein Issue auf GitHub eröffnen.
