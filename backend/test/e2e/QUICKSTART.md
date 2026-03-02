# E2E Test Suite - Quick Reference

## Start E2E Environment

```bash
# Full environment with all services
docker-compose -f docker-compose.e2e.yml up -d

# Or use automated test runner
./scripts/run_e2e_tests.sh
```

## Send Demo Emails

```bash
python scripts/send_demo_email.py
```

## Run Tests

```bash
cd backend

# All E2E tests
pytest test/e2e/ -v

# Specific markers
pytest test/e2e/ -m "rag"
pytest test/e2e/ -m "email"
pytest test/e2e/ -m "not slow"
```

## Demo Configuration

**IMAP:** localhost:3143 (user: demo@example.com)
**SMTP:** localhost:3025
**API:** http://localhost:33801

## Stop Environment

```bash
docker-compose -f docker-compose.e2e.yml down -v
```
