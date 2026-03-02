# Privacy Law E2E Tests

This directory contains E2E tests for the email assistant using **privacy law documents** (GDPR, CCPA) as test data.

> **Important**: These tests validate the **generic email assistant** functionality. The privacy laws are used purely as **test data** to demonstrate the system works with structured legal documents. The email assistant itself remains domain-agnostic.

## Test Files

### `test_privacy_simple_query.py`
Tests simple single-article queries:
- **GDPR Article 6**: Legal basis for processing employee data
- **GDPR Article 17**: Right to be forgotten

### `test_privacy_multi_context.py`
Tests multi-article context queries:
- **Data Breach Notification**: Requires Art. 33 + Art. 34 GDPR
- **Consent Requirements**: Requires Art. 7 + Art. 13 GDPR

## Running the Tests

### Prerequisites
1. Start E2E environment:
   ```bash
   ./scripts/run_e2e_tests.sh
   ```

2. Or manually with docker-compose:
   ```bash
   docker-compose -f docker-compose.e2e.yml up -d
   ```

### Run Privacy Tests
```bash
# All privacy tests
cd backend
python -m pytest test/e2e/ -v -m privacy

# Specific test file
python -m pytest test/e2e/test_privacy_simple_query.py -v

# Single test
python -m pytest test/e2e/test_privacy_simple_query.py::test_simple_gdpr_query -v
```

## Test Data

Test data is located in `/e2e_data/privacy/`:
- `gdpr/` - GDPR articles (EU privacy law)
- `usa/` - CCPA/CPRA (California privacy law)
- `international/` - Cross-jurisdiction documents

Query definitions: `/e2e_data/test_queries_privacy.json`

## What These Tests Validate

1. **Document Ingestion**: Upload and process legal documents
2. **RAG Query**: Retrieve relevant articles based on natural language queries
3. **Multi-Article Context**: Handle queries requiring multiple sources
4. **Citation Accuracy**: Verify correct article references in results
5. **Timeline Extraction**: Extract specific details (e.g., "72 hours")

## Success Criteria

- ✅ Documents upload successfully
- ✅ Queries return relevant results (Top-3 accuracy > 80%)
- ✅ Correct article references found
- ✅ Query time < 2 seconds
- ✅ Multi-article queries return all relevant sources

## Notes

- Tests use **simplified GDPR excerpts** for speed
- Full GDPR/CCPA documents can be added to `/e2e_data/privacy/`
- Tests are **domain-agnostic** - same patterns work for any knowledge domain
