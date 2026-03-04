# PantheonMail — Deployment-Guide

Umfassender Leitfaden für Deployment und Betrieb von PantheonMail v5.0.

---

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Lokale Entwicklung](#lokale-entwicklung)
3. [Docker-Deployment](#docker-deployment)
4. [Modulare Architektur](#modulare-architektur)
5. [Production-Deployment](#production-deployment)
6. [Environment-Variablen](#environment-variablen)
7. [Datenbank-Migration](#datenbank-migration)
8. [Backup & Recovery](#backup--recovery)
9. [Monitoring & Logging](#monitoring--logging)
10. [Troubleshooting](#troubleshooting)

---

## Übersicht

### Deployment-Optionen

| Option | Beschreibung | Zielgruppe |
|--------|--------------|------------|
| **Lokal (ohne Docker)** | Python venv + npm | Development |
| **Docker (Single)** | Alle Services in einem Container | Testing |
| **Docker (Modular)** | Separate Container pro Service | Development/Production |
| **Docker (Full)** | Mit allen externen Diensten | Production |

### Empfohlene Hardware

| Umgebung | CPU | RAM | Storage |
|----------|-----|-----|---------|
| **Development** | 4 Kerne | 8 GB | 20 GB |
| **Production** | 8 Kerne | 16 GB | 50 GB+ |
| **LLM (lokal)** | 8+ Kerne | 32 GB+ | 100 GB+ |

---

## Lokale Entwicklung

### Voraussetzungen

```bash
# Python 3.11+
python3 --version

# Node.js 20+
node --version

# Ollama (optional, für lokale LLMs)
ollama --version
```

### Backend einrichten

```bash
# 1. Repository klonen
git clone https://github.com/YOUR_USERNAME/mail_modul_fiat.git
cd mail_modul_fiat

# 2. Virtuelle Umgebung erstellen
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Environment konfigurieren
cp .env.example .env
# .env bearbeiten: DEV_MODE=true, LLM_PROVIDER, etc.

# 5. Backend starten
uvicorn src.main:app --reload --port 33800
```

### Externe Dienste (Docker)

```bash
# Nur ChromaDB, Redis (ohne Backend)
cd ..
docker-compose up chromadb redis -d

# Status prüfen
docker-compose ps
```

### Frontend einrichten

```bash
# 1. Frontend-Verzeichnis
cd frontend

# 2. Abhängigkeiten installieren
npm install

# 3. Frontend starten
npm start
```

**Erwartete Ausgabe:**
```
✓ Backend: http://localhost:33800
✓ Frontend: http://localhost:3000
✓ Electron App öffnet sich automatisch
```

---

## Docker-Deployment

### Single-Container (Alle Services)

```bash
# Alle Services in einem Docker-Compose
docker-compose up --build
```

**Services:**
- Backend (Port 33800)
- ChromaDB (Port 38000)
- Redis (Port 36379)
- Ollama (Port 11434)
- Celery Worker

### Full-Stack (Empfohlen für Testing)

```bash
# docker-compose-full.yml verwenden
docker-compose -f docker-compose-full.yml up --build -d

# Logs beobachten
docker-compose logs -f
```

### Container-Status prüfen

```bash
# Alle Container anzeigen
docker-compose ps

# Einzelnen Container-Log
docker-compose logs backend

# Health-Check
curl http://localhost:33800/api/health
```

---

## Modulare Architektur

### RAG-Modul separat betreiben

**Vorteile:**
- RAG-Modul kann von mehreren Apps genutzt werden
- Unabhängige Skalierung
- Einfachere Wartung

**Schritt 1: RAG-Modul starten**

```bash
# docker-compose-modular.yml
docker-compose -f docker-compose-modular.yml up rag_module rag_chromadb -d
```

**Schritt 2: Email Assistant mit externem RAG**

```bash
# In .env setzen:
EXTERNAL_RAG_ENABLED=true
EXTERNAL_RAG_URL=http://localhost:8080
EXTERNAL_RAG_TIMEOUT=60

# Email Assistant starten
docker-compose -f docker-compose-modular.yml up email_assistant -d
```

### Netzwerk-Konfiguration

```yaml
# docker-compose-modular.yml
networks:
  rag_network:
    driver: bridge
  email_network:
    driver: bridge

services:
  rag_module:
    networks:
      - rag_network
  
  email_assistant:
    networks:
      - rag_network
      - email_network
```

---

## Production-Deployment

### 1. JWT-Authentifizierung aktivieren

```bash
# .env für Production
DEV_MODE=false
JWT_SECRET_KEY=<sicherer_key>

# JWT_SECRET_KEY generieren
openssl rand -hex 32
# Ausgabe: a1b2c3d4e5f6... (64 Zeichen)
```

### 2. Ersten Admin-User anlegen

```bash
# Nach dem Start
curl -X POST http://localhost:33800/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "sicheres_passwort_123"
  }'
```

### 3. HTTPS konfigurieren (Reverse Proxy)

**Nginx-Konfiguration:**

```nginx
server {
    listen 443 ssl http2;
    server_name mail.example.com;

    ssl_certificate /etc/letsencrypt/live/mail.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mail.example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:33800;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket Support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# HTTP → HTTPS Redirect
server {
    listen 80;
    server_name mail.example.com;
    return 301 https://$server_name$request_uri;
}
```

### 4. SSL-Zertifikat (Let's Encrypt)

```bash
# Certbot installieren
sudo apt install certbot python3-certbot-nginx

# Zertifikat beantragen
sudo certbot --nginx -d mail.example.com

# Auto-Renewal prüfen
sudo certbot renew --dry-run
```

### 5. Docker-Compose für Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    image: mail-modul-fiat:latest
    restart: always
    environment:
      - DEV_MODE=false
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_URL=sqlite:///./data/app.db
    volumes:
      - ./data:/app/data
      - ./uploads:/app/data/uploads
    networks:
      - fiat_network
    depends_on:
      - chromadb
      - redis

  chromadb:
    image: chromadb/chroma:0.5.23
    restart: always
    volumes:
      - chroma_data:/chroma/chroma
    networks:
      - fiat_network

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - fiat_network

volumes:
  chroma_data:
  redis_data:

networks:
  fiat_network:
    driver: bridge
```

### 6. Deployment durchführen

```bash
# 1. Image bauen
docker-compose -f docker-compose.prod.yml build

# 2. Container starten
docker-compose -f docker-compose.prod.yml up -d

# 3. Status prüfen
docker-compose -f docker-compose.prod.yml ps

# 4. Logs beobachten
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Environment-Variablen

### Vollständige Referenz

```bash
# ==========================================
# DEVELOPMENT MODE
# ==========================================
DEV_MODE=false                    # true = Keine JWT-Auth (nur Development!)

# ==========================================
# SICHERHEIT (PFLICHT für Production)
# ==========================================
JWT_SECRET_KEY=<64_zeichen_random>  # openssl rand -hex 32

# ==========================================
# LLM KONFIGURATION
# ==========================================
LLM_PROVIDER=ollama               # ollama, openai, gemini, anthropic
LLM_MODEL=llama3:latest           # Modell-Name

# OpenAI (falls LLM_PROVIDER=openai)
OPENAI_API_KEY=sk-...

# Google Gemini (falls LLM_PROVIDER=gemini)
GOOGLE_API_KEY=AIza...

# Anthropic (falls LLM_PROVIDER=anthropic)
ANTHROPIC_API_KEY=sk-ant-...

# ==========================================
# EMBEDDING KONFIGURATION
# ==========================================
EMBEDDING_PROVIDER=ollama         # ollama, openai
EMBEDDING_MODEL=nomic-embed-text:latest

# ==========================================
# EMAIL KONFIGURATION
# ==========================================
EMAIL_PROVIDER=imap               # imap, gmail
EMAIL_USER=you@example.com
EMAIL_PASSWORD=app-password
IMAP_HOST=imap.example.com
IMAP_PORT=993

# Gmail OAuth2 (falls EMAIL_PROVIDER=gmail)
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REFRESH_TOKEN=...

# ==========================================
# FIAT EDITION
# ==========================================
MAIL_EDITION_LEAN=true            # Performance-Optimierung
EDITION=team                      # developer, team, enterprise

# ==========================================
# INFRASTRUKTUR
# ==========================================
DATABASE_URL=sqlite:///./data/app.db
CHROMA_HOST=http://chromadb:8000
CHROMA_PORT=8000
REDIS_HOST=redis
REDIS_PORT=6379
OLLAMA_HOST=http://ollama:11434

# ==========================================
# EXTERNES RAG (optional)
# ==========================================
EXTERNAL_RAG_ENABLED=false
EXTERNAL_RAG_URL=http://localhost:8080
EXTERNAL_RAG_API_KEY=
EXTERNAL_RAG_TIMEOUT=60

# ==========================================
# RAG EINSTELLUNGEN
# ==========================================
RERANKER_ENABLED=true
USE_PARENT_RETRIEVER=false
USE_ADVANCED_PIPELINE=false
CHUNK_SIZE=512
CHUNK_OVERLAP=128

# ==========================================
# CACHE PFADE (Mobile-Daten-Schonung)
# ==========================================
HF_HOME=/app/data/cache/huggingface
NLTK_DATA=/app/data/cache/nltk
DOCLING_CACHE=/app/data/cache/docling

# ==========================================
# LOGGING
# ==========================================
LOG_LEVEL=INFO                    # DEBUG, INFO, WARN, ERROR
DEBUG=false

# ==========================================
# WEBSOCKET KONFIGURATION
# ==========================================
WEBSOCKET_HEARTBEAT_INTERVAL=30
WEBSOCKET_HEARTBEAT_TIMEOUT=90
WEBSOCKET_AUTH_REQUIRED=false
WEBSOCKET_LOCALHOST_ONLY=true
WEBSOCKET_IDLE_TIMEOUT=300
WEBSOCKET_MAX_QUEUE_SIZE=16

# ==========================================
# HEALTH MONITOR
# ==========================================
HEALTH_CHECK_INTERVAL=5
HEALTH_EVENT_DEBOUNCE=2
HEALTH_MAX_SUBSCRIBERS=10

# ==========================================
# RATE LIMITING
# ==========================================
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_EMAIL=30/minute
RATE_LIMIT_RAG=50/minute
RATE_LIMIT_UPLOAD=10/minute
```

---

## Datenbank-Migration

### Alembic einrichten

```bash
# Backend-Verzeichnis
cd backend

# Alembic initialisieren (falls nicht vorhanden)
alembic init alembic

# Konfiguration bearbeiten
# alembic/alembic.ini:
# sqlalchemy.url = sqlite:///./data/app.db
```

### Migration erstellen

```bash
# Neue Migration erstellen
alembic revision --autogenerate -m "Add new_table"

# Migration anwenden
alembic upgrade head

# Migration zurückrollen
alembic downgrade -1
```

### Migration für Production

```bash
# 1. Backup erstellen
cp ./data/app.db ./data/app.db.backup.$(date +%Y%m%d)

# 2. Migration im Container
docker-compose exec backend alembic upgrade head

# 3. Erfolg prüfen
docker-compose exec backend alembic current
```

---

## Backup & Recovery

### Datenbank-Backup

```bash
# SQLite Backup
cp ./backend/data/app.db ./backups/app.db.$(date +%Y%m%d).bak

# ChromaDB Backup (Volume)
docker run --rm \
  -v mail_modul_fiat_rag_chroma_data:/source \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/chroma_data.$(date +%Y%m%d).tar.gz /source
```

### Redis Backup

```bash
# RDB Snapshot
docker-compose exec redis redis-cli SAVE

# RDB kopieren
docker cp mail_fiat_redis:/data/dump.rdb ./backups/dump.$(date +%Y%m%d).rdb
```

### Vollständiges Backup-Skript

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# SQLite
cp ./backend/data/app.db $BACKUP_DIR/app.db.$DATE.bak

# ChromaDB
docker run --rm \
  -v mail_modul_fiat_rag_chroma_data:/source \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/chroma_data.$DATE.tar.gz /source

# Redis
docker-compose exec redis redis-cli SAVE
docker cp mail_fiat_redis:/data/dump.rdb $BACKUP_DIR/dump.$DATE.rdb

# .env
cp .env $BACKUP_DIR/env.$DATE.bak

echo "Backup completed: $DATE"
```

### Recovery

```bash
# 1. Container stoppen
docker-compose down

# 2. Datenbank wiederherstellen
cp ./backups/app.db.20260301.bak ./backend/data/app.db

# 3. ChromaDB wiederherstellen
docker run --rm \
  -v mail_modul_fiat_rag_chroma_data:/target \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/chroma_data.20260301.tar.gz -C /target

# 4. Redis wiederherstellen
docker cp ./backups/dump.20260301.rdb mail_fiat_redis:/data/dump.rdb

# 5. Container starten
docker-compose up -d
```

---

## Monitoring & Logging

### Log-Konfiguration

```python
# src/config/logging.py
LOG_LEVEL=INFO  # DEBUG, INFO, WARN, ERROR

# Log-Format
{
    "timestamp": "...",
    "level": "INFO",
    "message": "...",
    "module": "email_service"
}
```

### Docker-Logs

```bash
# Alle Logs
docker-compose logs -f

# Einzelner Service
docker-compose logs -f backend

# Letzte 100 Zeilen
docker-compose logs --tail=100 backend

# Logs in Datei
docker-compose logs backend > backend.log
```

### Health-Check Endpunkte

```bash
# API Health
curl http://localhost:33800/api/health

# ChromaDB Health
curl http://localhost:38000/api/v1/heartbeat

# Ollama Health
curl http://localhost:11434/api/tags
```

### Prometheus Metrics

```bash
# Metrics-Endpunkt
curl http://localhost:33800/metrics

# Metriken:
# - http_requests_total
# - http_request_duration_seconds
# - rag_queries_total
# - llm_tokens_total
```

### Grafana Dashboard (Optional)

```yaml
# docker-compose-monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## Troubleshooting

### Backend startet nicht

```bash
# Logs prüfen
docker-compose logs backend

# Häufige Fehler:
# 1. JWT_SECRET_KEY nicht gesetzt
# 2. Port 33800 belegt
# 3. Datenbank-Pfade ohne Schreibrechte

# Lösung:
# 1. .env prüfen
# 2. Port freigeben: sudo lsof -i :33800
# 3. Berechtigungen: chmod -R 755 ./backend/data
```

### ChromaDB Verbindungsfehler

```bash
# ChromaDB Logs
docker-compose logs chromadb

# Volume-Probleme
docker-compose down -v
docker-compose up --build

# Health-Check
curl http://localhost:38000/api/v1/heartbeat
```

### Ollama Timeout

```bash
# Ollama läuft?
docker-compose ps ollama

# Models vorhanden?
docker-compose exec ollama ollama list

# Models nachpullen
docker-compose exec ollama ollama pull llama3:latest

# Host-Netzwerk (Linux)
# In .env: OLLAMA_HOST=http://host.docker.internal:11434
# Funktioniert nicht auf Linux → Ollama-Container verwenden
```

### Redis Connection Refused

```bash
# Redis Logs
docker-compose logs redis

# Redis CLI
docker-compose exec redis redis-cli ping
# Sollte: PONG

# Volume-Probleme
docker-compose down -v
docker-compose up -d redis
```

### Frontend zeigt weißen Bildschirm

```bash
# Frontend-Cache leeren
rm -rf frontend/.webpack
rm -rf frontend/node_modules/.cache

# Neu bauen
cd frontend
npm install
npm start

# Electron DevTools
# Strg+Shift+I (Linux/Windows)
# Cmd+Option+I (Mac)
```

### JWT-Auth-Probleme

```bash
# DEV_MODE prüfen
grep DEV_MODE .env

# Token generieren
curl -X POST http://localhost:33800/api/v1/auth/login \
  -d "username=admin&password=..."

# Token im Header
curl -H "Authorization: Bearer <token>" \
  http://localhost:33800/api/v1/email/inbox

# Token verfallen?
# → Refresh Token verwenden oder neu login
```

### Performance-Probleme

```bash
# Ressourcen-Nutzung
docker stats

# Langsame Queries identifizieren
# LOG_LEVEL=DEBUG in .env

# Caching aktivieren
# Redis Cache für Embeddings und Queries

# LLM-Provider wechseln
# Von Ollama zu OpenAI (schneller, aber kostet)
```

---

## Lizenz

Dieses Projekt steht unter der AGPL-3.0 Lizenz.
