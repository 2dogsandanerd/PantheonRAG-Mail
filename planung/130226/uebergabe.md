# Übergabe - RAG Migration - 12.02.2026 -> 13.02.2026

## Status Quo
- **Phase 1 (Code Migration)**: Abgeschlossen. RAG-Funktionalität ist in `RAGClient` und `ExternalRAGConnector` extrahiert. Factory-Pattern (`get_rag_service`) ist implementiert.
- **Phase 2 (Testing)**: Laufend. `DoclingService` Tests sind grün. Integrationstests sind rot.

## Erledigt
1. **DoclingService**: Async-Logic korrigiert, Metadaten-Fixes implementiert, Tests laufen durch.
2. **Infrastructure**: `dependencies.py` Import-Reihenfolge korrigiert (`NameError` behoben).
3. **Configuration**: `.lower()` Bug bei Boolean-Werten in `get_rag_service` gefixt.
4. **Consistency**: `RAGResponse.fail()` standardisiert und Alias für Legacy-Code hinzugefügt.

## Offene Probleme (Blocker)
1. **QueryService Crash**:
   - Error: `'NoneType' object has no attribute 'get'` in `QueryService.get_query_engine` (Zeile 326).
   - Verdacht: Embedding-Manager oder Collection-Initialization schlägt fehl und gibt `None` zurück, was nicht abgefangen wird.
   - Datei: `backend/src/core/services/query_service.py`

2. **Ollama Dependency**:
   - Error: `assert 0 > 0` in `test_rag_integration.py`.
   - Ursache: Tests erwarten eine laufende Ollama-Instanz für Embeddings. Wenn diese nicht erreichbar ist oder Timeouts wirft, schlagen die Tests fehl, da keine Embeddings generiert werden.
   - Lösung benötigt: Mocking der Embeddings für Integrationstests oder sicherstellen der Ollama-Verfügbarkeit im CI/Test-Env.

## Nächste Schritte
1. **QueryService Debuggen**: Den `NoneType`-Fehler in `get_query_engine` finden und beheben.
2. **Mocking einbauen**: Eine Strategie implementieren, damit Tests auch ohne live Ollama laufen (z.B. Fake-Embeddings).
3. **End-to-End Verifikation**: Wenn Tests grün sind, manuellen Test (oder E2E Skript) laufen lassen.

## Relevante Dateien
- `backend/src/core/services/query_service.py` (Hier liegt der Bug)
- `backend/test/test_integration_tax_advisor.py` (Reproduziert den Bug)
- `backend/src/services/draft_service.py` (Logging hinzugefügt)
