"""
E2E Test Suite for Mail Modul Fiat

This module contains end-to-end tests that test the complete system
without mocks - using real services (ChromaDB, Redis, GreenMail).
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

# E2E Test Markers
E2E_MARKERS = {
    "rag": "tests requiring ChromaDB",
    "email": "tests requiring GreenMail IMAP/SMTP",
    "llm": "tests requiring LLM (Ollama)",
    "slow": "slow tests (>30s)",
    "integration": "full integration tests",
}
