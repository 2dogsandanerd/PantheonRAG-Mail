# Gmail RAG Assistant - FastAPI

AI-powered Email Assistant with RAG and Multi-Provider LLM Support.

## Quick Start

### 1. Configure Environment
Copy `.env.example` to `.env` and fill in your API keys if you want to use providers other than Ollama.

### 2. Start Services
Make sure the services from the original Streamlit project are running (Ollama, ChromaDB).
Then, start the new services for this project:
```bash
docker compose up -d
```
This will start the FastAPI app, Redis, and the Celery workers.

### 3. Run FastAPI (if not using docker-compose for the app)
```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.main:app --reload
```

### 4. Access API
- API: http://localhost:33800
- Interactive Docs: http://localhost:33800/docs
- Health Check: http://localhost:33800/api/health

### 5. Register a User
To use the protected endpoints, you must first register a user:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d 
'{'
    "username": "admin",
    "email": "admin@example.com",
    "password": "secure123"
  }'
```

## Testing

To run the test suite, ensure you have the dev dependencies installed:
```bash
pytest --cov=src
```

## Project Structure

```
mail_modul_fiat/backend/
├── src/
│   ├── core/              # Business logic from Streamlit
│   ├── services/          # SQLAlchemy-adapted services
│   ├── database/          # Models & database setup
│   ├── api/v1/            # REST API endpoints
│   ├── worker/            # Celery background worker setup
│   └── main.py            # FastAPI application
├── test/                  # Pytest tests
├── docs/                  # Documentation
└── data/                  # Redis data (Chroma and SQLite are in other project)
```
