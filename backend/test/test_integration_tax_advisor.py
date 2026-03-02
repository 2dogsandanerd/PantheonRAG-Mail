import os
import pytest
import sys
from pathlib import Path
import json
from typing import Dict, Any, List
import asyncio

# Set an in-memory SQLite database for testing
os.environ["lea_database_url"] = "sqlite:///file::memory:?cache=shared"

# Add backend to path
# This is a common pattern in the project's test files
sys.path.insert(0, str(Path(__file__).parent.parent))

# Enable pytest-asyncio for the entire module
pytest_plugins = ('pytest_asyncio',)

from src.services.external_rag_connector import get_rag_service
from src.services.draft_service import DraftService
from src.core.services.query_service import QueryService
from src.services.learning_manager import LearningManager
import src.database.database as database # Import the module
from src.database.database import init_db, engine # Keep init_db and engine for direct use
from src.services.config_service import config_service
from src.core.indexing_service import Document as IndexingDocument
from loguru import logger
import sys # Import sys for stderr
from src.core.chroma_manager import get_chroma_manager # Import the getter function

logger.add(sys.stderr, level="DEBUG")

# --- Test Data ---
# Adapted from create_tax_advisor_test_data.py and test_tax_advisor_drafts.py

TAX_LAW_DATA = [
    {
        "content": """Einkommensteuer-Sonderausgaben: § 35a EStG - Haushaltsnahe Dienstleistungen
        Voraussetzungen: Die Dienstleistung muss im privaten Haushalt des Steuerpflichtigen ausgeführt werden.
        Maximal 20% von 20.000 € (also max. 4.000 €) jährlich steuerlich absetzbar.
        Beispiele: Putzfrau, Gartenpflege, Winterdienst, Handwerkerarbeiten im Haushalt.""",
        "metadata": {"law_section": "§ 35a EStG", "category": "Sonderausgaben", "type": "haushaltsnahe_dienstleistungen"}
    },
    {
        "content": """Spendenabzug und steuerliche Förderung nach § 10b EStG.
        Förderungsfähige Organisationen sind z.B. Wohlfahrtsverbände oder Umweltschutzorganisationen.
        Bis 300 € ist keine Spendenbescheinigung erforderlich. Maximal 20% des Gesamtbetrags der Einkünfte sind absetzbar.""",
        "metadata": {"law_section": "§ 10b EStG", "category": "Sonderausgaben", "type": "spenden"}
    },
    {
        "content": """Grundsteuerreform 2025. Neue Grundsteuerabgabe ab 2025.
        Berechnung anhand des Grundsteuerwerts und des Hebesatzes der Gemeinde.
        Die neue Regelung führt in vielen Fällen zu höheren Abgaben.""",
        "metadata": {"law_section": "Grundsteuer", "category": "Grundsteuer", "type": "neuregelung"}
    },
    {
        "content": """Kinderfreibetrag und Kindergeld 2025.
        Kinderfreibetrag (pro Kind): 8.640 € jährlich.
        Kindergeld (pro Kind): 250 € monatlich.
        Beide Leistungen können nicht gleichzeitig bezogen werden (Günstigerprüfung).""",
        "metadata": {"law_section": "Kinderfreibetrag", "category": "Familienförderung", "type": "kinder"}
    }
]

CLIENT_DATA = [
    {
        "content": """Mandant: Hans Müller GmbH, Mandanten-Nr: M-001.
        Branche: Handwerk (Malerbetrieb). Wichtigste Themen: Umsatzsteuervoranmeldung, Jahresabschluss.""",
        "metadata": {"mandant_id": "M-001", "category": "GmbH", "branche": "Handwerk"}
    },
    {
        "content": """Mandant: Familie Weber, Mandanten-Nr: M-002.
        Beschreibung: Verheiratetes Ehepaar mit 2 Kindern (Lisa, 8; Max, 5).
        Ehemann: Michael Weber (Arzt, Einkommen: 120.000 €).
        Ehefrau: Sabine Weber (Freiberuflerin, Einkommen: 45.000 €).
        Gesamteinkommen ca. 165.000 €.
        Wichtigste Themen: Einkommensteuererklärung, Kinderfreibeträge.""",
        "metadata": {"mandant_id": "M-002", "category": "Privat", "familienstand": "verheiratet"}
    }
]

NOTICE_DATA = [
    {
        "content": """Einkommensteuerbescheid 2023 für Michael und Sabine Weber (Steuer-Nr: 123/456/789).
        Zu versteuerndes Einkommen: 140.000 €. Festgesetzte Einkommensteuer: 32.500 €.""",
        "metadata": {"steuernummer": "123/456/789", "bescheid_typ": "ESt-Bescheid", "jahr": 2023}
    },
    {
        "content": """Grundsteuerbescheid 2024 für Immobilie Musterstraße 12.
        Grundsteuerbetrag: 1.102,50 €. Fälligkeit: 15.06.2024.""",
        "metadata": {"steuernummer": "456/789/123", "bescheid_typ": "Grundsteuerbescheid", "jahr": 2024}
    }
]

TEST_EMAILS = [
    pytest.param(
        {
            "sender": "michael.weber@email.de",
            "subject": "Frage zum Kinderfreibetrag 2025",
            "body": "Sehr geehrte Damen und Herren, wir haben zwei Kinder und ein gemeinsames Einkommen von ca. 165.000 €. Lohnt sich der Kinderfreibetrag für uns mehr als das Kindergeld?",
        },
        ["Kinderfreibetrag", "8.640 €", "Günstigerprüfung"],
        ["test_steuerrecht"],
        id="kinderfreibetrag_weber"
    ),
    pytest.param(
        {
            "sender": "info@mueller-gmbh.de",
            "subject": "Haushaltsnahe Dienstleistungen",
            "body": "Guten Tag, kann ich die Kosten für eine Putzkraft in meinem Privathaus absetzen?",
        },
        ["haushaltsnahe", "§ 35a EStG", "Putzfrau"],
        ["test_steuerrecht"],
        id="haushaltsnahe_dienstleistungen_mueller"
    ),
    pytest.param(
        {
            "sender": "michael.weber@email.de",
            "subject": "Infos zu unserem Steuerbescheid",
            "body": "Hallo, könnten Sie uns kurz die Eckdaten unseres letzten Einkommensteuerbescheids für 2023 zusammenfassen?",
        },
        ["123/456/789", "140.000 €", "32.500 €"],
        ["test_bescheide", "test_mandanten"], # Should find client Weber and their notice
        id="steuerbescheid_weber"
    )
]

@pytest.mark.integration
@pytest.mark.asyncio
class TestTaxAdvisorIntegration:
    """
    Integration test suite for the tax advisor RAG and draft generation workflow.
    This test class simulates the entire process from data ingestion to draft generation.
    """
    # These will be set by the fixture on 'self'
    rag_client: Any
    draft_service: DraftService
    db_session: Any 

    test_collections: List[str] = ["test_steuerrecht", "test_mandanten", "test_bescheide"]

    @pytest.fixture(scope="class", autouse=True)
    async def setup_teardown_class_fixture(self, request):
        """
        Fixture for setting up and tearing down the test environment for the class.
        """
        logger.info("Setting up test class: Initializing services and RAG collections.")
        
        # --- MOCKING START ---
        from unittest.mock import patch, MagicMock, AsyncMock
        from llama_index.core.embeddings import MockEmbedding
        from llama_index.core.llms import MockLLM, LLMMetadata
        
        # Patch EmbeddingManager to return MockEmbedding
        embed_patcher = patch('src.core.embedding_manager.EmbeddingManager.get_embeddings')
        mock_get_embeddings = embed_patcher.start()
        mock_embedding = MockEmbedding(embed_dim=768)
        mock_get_embeddings.return_value = mock_embedding
        
        # Configure MockLLM to return a valid response
        # Use a simple dummy class to avoid MagicMock/AsyncMock issues
        class DummyLLM:
            def __init__(self):
                self.system_prompt = None
                
            def complete(self, prompt, **kwargs):
                return mock_response
            async def acomplete(self, prompt, **kwargs):
                return mock_response
            def predict(self, prompt, **kwargs):
                return str(mock_response)
            async def apredict(self, prompt, **kwargs):
                return str(mock_response)
            @property
            def metadata(self):
                return LLMMetadata(context_window=4096, num_output=512, model_name="mock-model")

        # Create a mock response object that behaves like CompletionResponse
        # It needs __str__ to return the text and text attribute
        mock_response = MagicMock()
        mock_response.__str__.return_value = "DRAFT | Sehr geehrter Herr Weber, bezüglich Ihrer Anfrage zum Kinderfreibetrag..."
        mock_response.text = "DRAFT | Sehr geehrter Herr Weber, bezüglich Ihrer Anfrage zum Kinderfreibetrag..."

        mock_llm = DummyLLM()

        # Patch get_llm GLOBALLY in the definition module
        # This is necessary because QueryService imports it locally inside answer_query
        llm_patcher = patch('src.core.llm_singleton.get_llm')
        mock_get_llm = llm_patcher.start()
        mock_get_llm.return_value = mock_llm
        
        # Patch get_llm in QueryService module where it is already imported globally
        # This is necessary for get_query_engine which uses the global import
        qs_llm_patcher = patch('src.core.services.query_service.get_llm')
        mock_qs_get_llm = qs_llm_patcher.start()
        mock_qs_get_llm.return_value = mock_llm
        
        # Patch get_llm in DraftService module where it is imported
        ds_llm_patcher = patch('src.services.draft_service.get_llm')
        mock_ds_get_llm = ds_llm_patcher.start()
        mock_ds_get_llm.return_value = mock_llm

        # Patch EvaluationService.evaluate_query to prevent Ragas errors
        eval_patcher = patch('src.core.evaluation.eval_service.EvaluationService.evaluate_query')
        mock_evaluate_query = eval_patcher.start()
        mock_evaluate_query.return_value = None

        # Register patchers for teardown
        request.cls._embed_patcher = embed_patcher
        request.cls._llm_patcher = llm_patcher
        request.cls._qs_llm_patcher = qs_llm_patcher
        request.cls._ds_llm_patcher = ds_llm_patcher
        request.cls._eval_patcher = eval_patcher
        # --- MOCKING END ---

        config = config_service.load_configuration()
        
        # Configure ChromaManager for in-memory mode for testing
        get_chroma_manager().configure(in_memory=True)

        # Add CHROMA_IN_MEMORY to config for testing
        config["CHROMA_IN_MEMORY"] = True
        # Set LLM_PROVIDER for testing purposes
        config["LLM_PROVIDER"] = "OLLAMA"
        # Force local RAG for this integration test
        config["EXTERNAL_RAG_ENABLED"] = "false"

        # Initialize RAG service and store on the class instance
        from src.services.external_rag_connector import get_rag_service
        request.cls.rag_client = await get_rag_service(config_override=config)
        
        # Initialize database for LearningManager
        # Pass the in-memory database URL directly to init_db
        await init_db(database_url="sqlite:///file::memory:?cache=shared")
        request.cls.db_session = database.AsyncSessionLocal() # Get a session instance from the module
        learning_manager = LearningManager(request.cls.db_session)
        # Initialize QueryService
        from src.core.embedding_manager import EmbeddingManager
        embedding_manager = EmbeddingManager(config_override=config)
        query_service = QueryService(
            chroma_manager=get_chroma_manager(),
            embedding_manager=embedding_manager,
            config=config
        )

        # Initialize DraftService and store on the class instance
        request.cls.draft_service = DraftService(
            rag_client=request.cls.rag_client,
            query_service=query_service,
            learning_manager=learning_manager,
            config_override=config
        )
        # Clean up any old test collections
        for coll_name in request.cls.test_collections:
            try:
                # Use top-level delete_collection
                await request.cls.rag_client.delete_collection(coll_name)
                logger.info(f"Cleaned up old collection: {coll_name}")
            except Exception:
                pass # Ignore if collection doesn't exist

        # Create and populate collections
        await request.cls._create_and_populate(request.cls, "test_steuerrecht", TAX_LAW_DATA)
        await request.cls._create_and_populate(request.cls, "test_mandanten", CLIENT_DATA)
        await request.cls._create_and_populate(request.cls, "test_bescheide", NOTICE_DATA)
        logger.info("Test collections created and populated successfully.")

        yield # This is where the tests run

        logger.info("Tearing down test class: Deleting RAG collections and closing DB session.")
        for coll_name in request.cls.test_collections:
            try:
                # Use top-level delete_collection
                await request.cls.rag_client.delete_collection(coll_name)
                logger.info(f"Deleted test collection: {coll_name}")
            except Exception as e:
                logger.error(f"Failed to delete collection {coll_name}: {e}")
        
        # Close the database session
        if request.cls.db_session:
            await request.cls.db_session.close()
        
        # Shutdown RAG client if needed
        if hasattr(request.cls.rag_client, "shutdown"):
            await request.cls.rag_client.shutdown()

        # Dispose of the engine to clean up connections
        if engine:
            await engine.dispose()
            
        # Stop patchers
        request.cls._embed_patcher.stop()
        request.cls._llm_patcher.stop()
        request.cls._qs_llm_patcher.stop()
        request.cls._ds_llm_patcher.stop()
        request.cls._eval_patcher.stop()

    async def _create_and_populate(self, name: str, data: List[Dict[str, Any]]):
        """Helper method to create and populate a collection."""
        # Use top-level create_collection
        response = await self.rag_client.create_collection(name)
        assert response.is_success if hasattr(response, "is_success") else response.get("success"), f"Failed to create collection {name}"

        # Convert dicts to Document objects for the indexing service
        docs_to_index = [
            IndexingDocument(content=item["content"], metadata=item["metadata"], doc_id=f"{name}_{i}")
            for i, item in enumerate(data)
        ]
        
        # Use the top-level index_documents method
        index_response = await self.rag_client.index_documents(
            collection_name=name,
            documents=docs_to_index
        )
        assert index_response.is_success if hasattr(index_response, "is_success") else index_response.get("success"), f"Failed to index documents into {name}"

    @pytest.mark.parametrize("email_data, expected_keywords, expected_collections", TEST_EMAILS)
    async def test_draft_generation_scenarios(self, email_data: Dict, expected_keywords: List[str], expected_collections: List[str]):
        """
        Tests various draft generation scenarios against the test collections.
        """
        logger.info(f"Testing draft generation for: {email_data['subject']}")

        # Set DRAFT_RAG_COLLECTIONS to use our test collections for this test
        # This ensures the draft service only queries our test collections
        self.draft_service.config["DRAFT_RAG_COLLECTIONS"] = ",".join(self.test_collections)

        result = await self.draft_service.generate_draft(
            email_data=email_data,
            user_id=1,
            use_rag=True
        )

        assert "error" not in result, f"Draft generation failed with error: {result.get('error')}"
        assert not result.get("no_answer_needed"), f"Draft was incorrectly classified as NO_ANSWER_NEEDED: {result.get('reason_category')}"
        
        rag_context = result.get("rag_context", "")
        assert rag_context, "RAG context is empty, but was expected."

        # Verify that the RAG context contains the expected information
        for keyword in expected_keywords:
            assert keyword.lower() in rag_context.lower(), f"Expected keyword '{keyword}' not found in RAG context."
        
        # Verify that the context came from the correct collection(s)
        for collection in expected_collections:
            assert f"[{collection.upper()}" in rag_context, f"Expected context from collection '{collection}' not found."

        logger.success(f"Successfully validated draft for: {email_data['subject']}")

    async def test_domain_routing_feature(self):
        """
        Tests that the domain routing feature correctly limits the collections being queried.
        """
        logger.info("Testing domain routing feature.")

        # 1. Define a domain that only includes 'test_bescheide'
        # Note: This directly manipulates self.draft_service.rag_domains for testing purposes.
        # In a real scenario, this would be loaded from rag_domains.json.
        self.draft_service.rag_domains = {
            "billing": {
                "collections": ["test_bescheide"]
            }
        }
        
        # 2. Create an email that requires info from 'test_steuerrecht' (Kinderfreibetrag)
        email_data = {
            "sender": "test@email.de",
            "subject": "Frage zum Kinderfreibetrag",
            "body": "Wie hoch ist der Kinderfreibetrag?"
        }

        # 3. Call generate_draft WITH the domain specified
        result = await self.draft_service.generate_draft(
            email_data=email_data,
            user_id=1,
            use_rag=True,
            domain="billing" # This should restrict the search to 'test_bescheide'
        )

        assert "error" not in result
        rag_context = result.get("rag_context", "")

        # 4. Assert that the context is from 'test_bescheide' and does NOT contain the answer
        # It's possible for rag_context to be empty if no relevant info is found in 'test_bescheide'
        # but it should definitely not contain info from 'test_steuerrecht'
        assert "[TEST_STEUERRECHT" not in rag_context, "Context from 'test_steuerrecht' should NOT be present when domain is 'billing'."
        assert "8.640 €" not in rag_context, "Specific info from 'test_steuerrecht' should not be found."
        
        # Optionally, check if any context from billing was found (e.g., a bescheid)
        if rag_context:
            assert "[TEST_BESCHEIDE" in rag_context, "Context should only come from 'test_bescheide' if any context is found."

        logger.success("Domain routing test passed: Correctly restricted search to the specified domain.")

        # Reset domains for other tests (though teardown_class will clean up anyway)
        # This is important if other tests in the same class might rely on the default rag_domains.json
        self.draft_service.rag_domains = self.draft_service._load_rag_domains()
