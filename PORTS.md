# 🔌 Ports & Netzwerkkonfiguration

## Übersicht der verwendeten Ports

PantheonMail verwendet **konfliktfreie Ports**, um Probleme bei paralleler Nutzung mit anderen Docker-Projekten zu vermeiden.

| Service | Externer Port | Interner Port | Protokoll | Hinweis |
|---------|---------------|---------------|-----------|---------|
| **Backend API** | **33800** | 33800 | HTTP | Haupt-API für alle Anfragen |
| **ChromaDB** | **38000** | 8000 | HTTP | Vektor-Datenbank (nicht 8000!) |
| **Redis** | **36379** | 6379 | TCP | Cache & Message Queue (nicht 6379!) |
| **Ollama** | **11434** | 11434 | HTTP | LLM-Server (geteilt mit ClawRAG) |

---

## Warum diese Ports?

### Problem mit Standard-Ports
- **Port 8000** wird von vielen Projekten verwendet:
  - ChromaDB (Standard)
  - FastAPI Development Server
  - MLflow
  - Und viele andere AI/ML-Tools

- **Port 6379** ist der Standard-Redis-Port:
  - Konflikte bei mehreren Redis-Instanzen
  - Häufig von anderen Diensten belegt

### Lösung
PantheonMail verwendet **3xxxx Ports** zur Vermeidung von Konflikten:
- `33800` → Backend (eindeutig)
- `38000` → ChromaDB (statt 8000)
- `36379` → Redis (statt 6379)
- `11434` → Ollama (bleibt Standard für Sharing mit ClawRAG)

---

## Zugriff von außen

### API Endpunkte
```bash
# Backend API
curl http://localhost:33800/api/health

# Interaktive API-Dokumentation
http://localhost:33800/docs

# ChromaDB (direkter Zugriff)
curl http://localhost:38000/api/v1/heartbeat

# Ollama (LLM-Abfragen)
curl http://localhost:11434/api/tags
```

### Docker-Netzwerk (interne Kommunikation)
Innerhalb des Docker-Netzwerks (`fiat_network`) verwenden die Container die **internen Ports**:
- `chromadb:8000`
- `redis:6379`
- `ollama:11434`
- `backend:33800`

---

## Parallele Nutzung mit anderen Projekten

### ✅ Kein Konflikt mit:
| Projekt | Ports | Status |
|---------|-------|--------|
| **ClawRAG** | 8080, 8000, 11434 | ✅ Kein Konflikt (Ollama shared) |
| **rag-auditor** | 8000 | ✅ Kein Konflikt |
| **Andere FastAPI-Projekte** | 8000, 8001, etc. | ✅ Kein Konflikt |

### ⚠️ Ollama Sharing
Ollama (Port 11434) wird **zentral** verwendet:
- mail_modul_fiat und ClawRAG teilen sich denselben Ollama-Container
- Modelle werden nur **einmal** heruntergeladen (`~/.ollama`)
- Spart Mobile-Daten und Speicherplatz

---

## Konfiguration anpassen

### Externe Ports ändern
Falls nötig, können die externen Ports in `docker-compose.yml` angepasst werden:

```yaml
services:
  chromadb:
    ports:
      - "38000:8000"  #Extern:38000 → Intern:8000
      # Auf "39000:8000" ändern für Port 39000
```

### Interne Ports (nicht empfohlen)
Die internen Ports sollten **nicht geändert** werden, da sie in der Codebase fest verankert sind.

---

## Fehlerbehebung

### Port bereits belegt
```bash
# Prüfen welcher Prozess einen Port belegt
sudo lsof -i :33800
# ODER
ss -tlnp | grep 33800

# Container stoppen die den Port blockieren
docker stop <container-name>
```

### Alle Ports freigeben
```bash
# Alle mail_modul_fiat Container stoppen
docker-compose down

# Alle Container mit diesen Ports finden
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "33800|38000|36379|11434"
```

---

## Quick Reference

```bash
# Health Check
curl http://localhost:33800/api/health

# ChromaDB Collections (direkt)
curl http://localhost:38000/api/v1/collections

# Ollama Models (direkt)
curl http://localhost:11434/api/tags

# Redis CLI
redis-cli -p 36379
```
