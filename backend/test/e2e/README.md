# E2E Test Suite for Mail Modul Fiat

## Overview

This E2E test suite tests the **complete system** without mocks, using real services:
- **GreenMail** - Mock IMAP/SMTP server for email testing
- **ChromaDB** - Real vector database for RAG
- **Redis** - For Celery task queue
- **Backend API** - Full FastAPI application

## Test Structure

```
backend/test/e2e/
├── __init__.py              # E2E module initialization
├── conftest.py              # Shared fixtures and configuration
├── test_health_flow.py      # Health checks and service status
├── test_rag_ingestion.py    # Document upload and processing
├── test_rag_query.py        # RAG queries with real ChromaDB
└── test_email_flow.py       # Email IMAP/SMTP with GreenMail
```

## Test Markers

- `@pytest.mark.e2e` - All E2E tests
- `@pytest.mark.rag` - Tests requiring ChromaDB
- `@pytest.mark.email` - Tests requiring GreenMail
- `@pytest.mark.slow` - Slow tests (>30s)
- `@pytest.mark.integration` - Full integration tests

## Quick Start

### 1. Start E2E Environment

```bash
# Start all services
docker-compose -f docker-compose.e2e.yml up -d

# Or use the test runner script
./scripts/run_e2e_tests.sh
```

### 2. Send Demo Emails

```bash
# Send sample demo emails to GreenMail
python scripts/send_demo_email.py

# Or send custom email
python scripts/send_demo_email.py "Subject" "Body" "recipient@example.com"
```

### 3. Run Tests

```bash
cd backend

# Run all E2E tests
pytest test/e2e/ -v

# Run specific test markers
pytest test/e2e/ -v -m "rag"
pytest test/e2e/ -v -m "email"
pytest test/e2e/ -v -m "not slow"

# Run with verbose output
pytest test/e2e/test_health_flow.py -v -s
```

## Demo Configuration

For user demonstrations, configure the app with these GreenMail settings:

**IMAP:**
- Host: `localhost`
- Port: `3143`
- User: `demo@example.com`
- Password: `any` (authentication disabled)

**SMTP:**
- Host: `localhost`
- Port: `3025`
- User: `demo@example.com`
- Password: `any`

## Services

### GreenMail (IMAP/SMTP)
- **Container:** `mail_modul_fiat_e2e_mail`
- **IMAP Port:** 3143
- **SMTP Port:** 3025
- **Status:** Check with `docker-compose -f docker-compose.e2e.yml logs greenmail`

### ChromaDB
- **Container:** `mail_modul_fiat_e2e_chroma`
- **Port:** 38001
- **API:** http://localhost:38001

### Redis
- **Container:** `mail_modul_fiat_e2e_redis`
- **Port:** 36380

### Backend
- **Container:** `mail_modul_fiat_e2e_backend`
- **Port:** 33801
- **Health:** http://localhost:33801/api/health

## Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose -f docker-compose.e2e.yml logs

# Restart
docker-compose -f docker-compose.e2e.yml down -v
docker-compose -f docker-compose.e2e.yml up -d
```

### Tests can't connect to services

```bash
# Verify services are running
curl http://localhost:33801/api/health
nc -z localhost 3143  # IMAP
nc -z localhost 3025  # SMTP
```

### Port conflicts

If ports are already in use, modify `docker-compose.e2e.yml`:
```yaml
ports:
  - "3144:3143"  # Change host port
```

## What Tests Verify

### Health Flow
- ✅ Backend API is accessible
- ✅ Services status endpoint works
- ✅ Dashboard stats available
- ✅ Configuration endpoints functional

### RAG Ingestion
- ✅ Collection creation
- ✅ Document upload (text files)
- ✅ Docling processing
- ✅ ChromaDB storage
- ✅ Document listing

### RAG Query
- ✅ Query empty collections
- ✅ Query with documents
- ✅ Advanced query options
- ✅ Domain-based routing
- ✅ LLM answer generation (if configured)

### Email Flow
- ✅ SMTP connection to GreenMail
- ✅ Send and receive emails
- ✅ Draft creation
- ✅ Inbox management
- ✅ Email threads

## Notes

- Tests use **real HTTP calls** - no mocks
- Tests create and cleanup test data automatically
- GreenMail resets between test runs (data not persisted)
- ChromaDB persists data in Docker volume (`chroma_e2e_data`)
