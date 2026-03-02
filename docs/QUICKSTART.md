# PantheonMail — Quickstart Guide

Get up and running in under 5 minutes.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Docker | 24+ | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Docker Compose | 2.20+ | bundled with Docker Desktop |
| Ollama | latest | [ollama.ai](https://ollama.ai) |

> **No Ollama?** You can also use OpenAI or Gemini — set `LLM_PROVIDER` accordingly in `.env`.

---

## Step 1: Clone

```bash
git clone https://github.com/YOUR_ORG/pantheonmail.git
cd pantheonmail
```

## Step 2: Configure

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` in your editor and set **at minimum**:

```env
# Generate with: openssl rand -hex 32
JWT_SECRET_KEY=REPLACE_ME

# Your IMAP email account
EMAIL_USER=you@example.com
EMAIL_PASSWORD=your-app-password-not-login-password
IMAP_HOST=imap.example.com
IMAP_PORT=993

# LLM (Ollama is default — runs locally)
LLM_PROVIDER=ollama
LLM_MODEL=llama3:latest
```

**Gmail users:** Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

## Step 3: Pull AI Models

```bash
# The language model (draft generation)
ollama pull llama3:latest

# The embedding model (RAG knowledge base)
ollama pull nomic-embed-text:latest
```

## Step 4: Start

```bash
docker-compose up --build
```

First startup takes 2–5 minutes (builds images, initializes database).

## Step 5: First Login

1. Open [http://localhost:33800/api/v1/docs](http://localhost:33800/api/v1/docs)
2. Use `POST /auth/register` to create your account
3. Use `POST /auth/login` to get your JWT token
4. Or open the Desktop UI: `cd frontend && npm install && npm start`

---

## What's Next?

### Upload Knowledge Documents

Go to the **RAG** section and upload your PDFs, Word docs, or text files.
The AI will use these when generating email replies.

```bash
# Via API
curl -X POST http://localhost:33800/api/v1/rag/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@/path/to/document.pdf" \
  -F "collection_name=my_knowledge_base"
```

### Fetch Your Inbox

```bash
curl http://localhost:33800/api/v1/email/inbox \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Generate a Draft

```bash
curl -X POST http://localhost:33800/api/v1/email/draft \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "client@example.com",
    "subject": "Question about your pricing",
    "body": "Hi, I would like to know more about your enterprise plan.",
    "thread_id": "thread_123",
    "use_rag": true
  }'
```

---

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common causes:
# - JWT_SECRET_KEY not set
# - Database permission issues
# - Port 33800 already in use
```

### Ollama connection refused
```bash
# Make sure Ollama is running
ollama serve

# Or in docker-compose.yml, check OLLAMA_HOST
# Default: http://host.docker.internal:11434
```

### IMAP authentication failed
- For Gmail: Enable "Less secure app access" or use App Passwords
- For Office 365: Use `outlook.office365.com` as IMAP host
- Check `EMAIL_PASSWORD` is an app-specific password

### Out of disk space (ChromaDB)
```bash
# Clean up old Docker volumes
docker-compose down -v
docker system prune -f
docker-compose up --build
```

---

## Modular Setup (Advanced)

Run the RAG module separately as a standalone service:

```bash
docker-compose -f docker-compose-modular.yml up --build
```

This is useful if you want to share one RAG service across multiple applications.

---

## Ports Reference

| Service | URL |
|---------|-----|
| Backend API | http://localhost:33800 |
| API Docs | http://localhost:33800/api/v1/docs |
| ChromaDB | http://localhost:38000 |
| Redis | localhost:36379 |
| Ollama | http://localhost:11434 |
