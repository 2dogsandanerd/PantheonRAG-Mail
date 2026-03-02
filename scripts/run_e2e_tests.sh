#!/bin/bash
# Mail Modul Fiat - E2E Test Runner
# Usage: ./scripts/run_e2e_tests.sh [test_marker]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.e2e.yml"
TEST_MARKER="${1:-e2e}"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Mail Modul Fiat - E2E Test Suite      ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Error: docker-compose not found${NC}"
    exit 1
fi

# Function to cleanup
cleanup() {
    echo ""
    # Ensure we are in the project root
    if [ -d "../backend" ]; then
        cd ..
    fi

    echo -e "${YELLOW}📋 Dumping backend logs...${NC}"
    docker-compose -f "$COMPOSE_FILE" logs --tail=100 backend
    
    echo ""
    echo -e "${YELLOW}🧹 Cleaning up...${NC}"
    docker-compose -f "$COMPOSE_FILE" down -v
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Start services
echo -e "${BLUE}🚀 Starting E2E test environment...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 15

# Check if backend is healthy
echo -e "${BLUE}🔍 Checking service health...${NC}"
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if curl -sf http://localhost:33801/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
        break
    fi
    echo -e "${YELLOW}  Attempt $attempt/$max_attempts: Waiting for backend...${NC}"
    sleep 5
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo -e "${YELLOW}📋 Checking logs...${NC}"
    docker-compose -f "$COMPOSE_FILE" logs backend
    exit 1
fi

# Check GreenMail
echo -e "${BLUE}📧 Checking GreenMail (IMAP/SMTP)...${NC}"
if nc -z localhost 3143 && nc -z localhost 3025; then
    echo -e "${GREEN}✅ GreenMail is ready (IMAP:3143, SMTP:3025)${NC}"
else
    echo -e "${RED}⚠️  GreenMail ports not accessible${NC}"
fi

# Check ChromaDB
echo -e "${BLUE}💾 Checking ChromaDB...${NC}"
if curl -sf http://localhost:38001/api/v1/heartbeat > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ChromaDB is ready${NC}"
else
    echo -e "${RED}⚠️  ChromaDB not responding${NC}"
fi

# Prepare Ollama Models (Skipped for Mock Mode)
echo -e "${BLUE}🤖 Using Mock Mode (Skipping Ollama pull)...${NC}"
# docker-compose -f "$COMPOSE_FILE" exec -T ollama ollama pull nomic-embed-text
# docker-compose -f "$COMPOSE_FILE" exec -T ollama ollama pull llama3.2

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  Running E2E Tests (marker: $TEST_MARKER)${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Run tests
cd backend
../venv/bin/python3 -m pytest test/e2e/ \
    -v \
    --tb=short \
    -m "$TEST_MARKER" \
    --color=yes \
    --capture=no

TEST_EXIT_CODE=$?

echo ""
echo -e "${BLUE}=========================================${NC}"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All E2E tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
fi

echo -e "${BLUE}=========================================${NC}"

exit $TEST_EXIT_CODE
