# Implementation Plan - RAG Mail Edition (Lean Strategy)

This plan outlines the "Surgical Cut" strategy to create a performant, modular "Mail Edition" of the RAG Enterprise Core. The goal is to evolve the Mail Assistant from a "Refinery" (Heavy multi-lane RAG) to a "Fiat" (Lean, fast, optimized for client-side) system while maintaining Six Sigma data quality.

## User Review Required

> [!IMPORTANT]
> **Breaking Change Proposal**: We will bypass the `Solomon` consensus engine and `Janus` routing by default for the Mail Edition, prioritizing `Docling` (`Goethe` lane) as the standard extraction method.

> [!WARNING]
> **No Graph Database**: Neo4j will be omitted for the Mail Edition. Entity relationships will be handled via metadata in ChromaDB/SQLite.

## Proposed Changes

### Core RAG Logic (Backend)

#### [MODIFY] [extraction_service.py](file:///mnt/dev/eingang/mail_modul_fiat/backend/src/services/extraction_service.py)
Update the extraction service to support the "Confidence-Trigger" strategy.
- Implement a "Lean Mode" flag (via environment variable `MAIL_EDITION_LEAN=true`).
- In Lean Mode, use `Docling` by default for all supported formats.
- Add a quality check post-extraction; only invoke the full RAG Core "Refinery" if the quality score is below a threshold (e.g., < 0.85).

#### [MODIFY] [docling_service.py](file:///mnt/dev/eingang/mail_modul_fiat/backend/src/services/docling_service.py)
Enhance the existing Docling service for better "Fiat Tuning".
- Optimize `pipeline_fast` for maximum speed on digital PDFs/emails.
- Ensure the `content` returned includes structural hints (headers, tables) that `Spock` can use for semantic boundary detection.

#### [NEW] [graph_lite_service.py](file:///mnt/dev/eingang/mail_modul_fiat/backend/src/services/graph_lite_service.py)
Implement the "Graph-Lite" strategy.
- Instead of Neo4j, use SQLite to store entity-relation facts (e.g., `Sender X` works for `Project Y`).
- Inject these facts as metadata into ChromaDB chunks during ingestion.

#### [MODIFY] [draft_service.py](file:///mnt/dev/eingang/mail_modul_fiat/backend/src/services/draft_service.py)
Optimize the RAG retrieval for the Mail Edition.
- Implement "Selective Spock": Use semantic chunking only for "Learning Pairs" (user corrections).
- For general emails, use a faster recursive character splitter or fixed-size chunking.
- Implement "Global Fact Injection": If the query matches an entity in the "Graph-Lite" service, inject associated facts into the LLM prompt.

### Infrastructure & Deployment

#### [MODIFY] [docker-compose.yml](file:///mnt/dev/eingang/mail_modul_fiat/docker-compose.yml)
- Remove observability services (Jaeger, Prometheus, Grafana) for the `mail-edition` profile.
- Add configuration for local-only execution and smaller LLM presets (Qwen2-7B).

## Verification Plan

### Automated Tests
- `pytest tests/test_lean_extraction.py`: Verify that Docling is used by default when `MAIL_EDITION_LEAN=true`.
- `pytest tests/test_graph_lite.py`: Verify entity relations are correctly stored in SQLite and retrieved during search.
- `benchmarking/run_fiat_vs_refinery.py`: Compare latency and resource usage between the "Lean" and "Full" modes.

### Manual Verification
- Ingest a complex email with attachments and verify that the draft is generated in < 5 seconds on standard client hardware.
- Correct a draft, verify it's stored as a "Learning Pair" with Spock semantic chunking, and ensure future drafts reflect the correction.
