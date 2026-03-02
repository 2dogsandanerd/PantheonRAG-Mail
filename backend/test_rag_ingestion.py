#!/usr/bin/env python3
"""
Testskript für die RAG-Ingestion mit verschiedenen Dateitypen
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List
import json

# Lade Umgebungsvariablen
from dotenv import load_dotenv
load_dotenv()

# Setze die Umgebungsvariable für Docling-Verwendung
import os
os.environ["USE_DOCLING_INGESTION"] = "true"

# Wird vom Backend-Verzeichnis ausgeführt, daher ist src direkt verfügbar
# PYTHONPATH wurde bereits gesetzt

from src.core.rag_client import RAGClient
from src.core.docling_loader import DoclingLoader, DoclingLoaderFactory
from src.core.indexing_service import Document, ChunkConfig


async def test_ingestion_with_various_types():
    """Testet die Ingestion mit verschiedenen Dateitypen"""
    
    # Konfiguration für RAG-Client
    config = {
        "CHROMA_HOST": os.getenv("CHROMA_HOST", "127.0.0.1"),
        "CHROMA_PORT": int(os.getenv("CHROMA_PORT", 33801)),
        "CHROMA_IN_MEMORY": os.getenv("CHROMA_IN_MEMORY", "False").lower() == "true",
        "OLLAMA_HOST": os.getenv("OLLAMA_HOST", "127.0.0.1"),
        "OLLAMA_PORT": int(os.getenv("OLLAMA_PORT", 11434)),
        "DEFAULT_EMBEDDING_MODEL": os.getenv("DEFAULT_EMBEDDING_MODEL", "nomic-embed-text")
    }
    
    print("Erstelle RAG-Client...")
    rag_client = RAGClient(config)
    
    # Teste verschiedene Dateien aus dem neu erstellten Testdaten-Verzeichnis
    # Gehe von backend-Verzeichnis aus
    test_files_dir = Path("../backend/test_data_extended")
    
    # Durchlaufe alle Dateien in den Ordnern
    file_extensions = ["*.docx", "*.xlsx", "*.csv", "*.json", "*.txt"]
    test_files = []
    
    for ext in file_extensions:
        test_files.extend(list(test_files_dir.rglob(ext)))
    
    print(f"Teste Ingestion mit {len(test_files)} verschiedenen Dateitypen...")
    
    collection_name = "test_collection_extended"
    
    # Lösche die Collection falls sie bereits existiert
    response = await rag_client.delete_collection(collection_name)
    if not response.is_success:
        print(f"Warnung: Konnte Collection nicht löschen - {response.error}")
    
    # Erstelle eine neue Collection
    response = await rag_client.create_collection(collection_name)
    if not response.is_success:
        print(f"Fehler beim Erstellen der Collection: {response.error}")
        await rag_client.shutdown()
        return
    
    print(f"Collection '{collection_name}' erfolgreich erstellt")
    
    # Teste die Ingestion für verschiedene Dateitypen
    successful_ingests = 0
    for i, file_path in enumerate(test_files[:10]):  # Teste die ersten 10 Dateien
        print(f"\n[{i+1}/{min(10, len(test_files))}] Verarbeite Datei: {file_path.name}")
        
        try:
            # Verwende DoclingLoader für die Datei
            loader = DoclingLoaderFactory.create_loader(str(file_path))
            
            # Lade die Dokumente
            llama_docs = loader.load()
            
            print(f"  -> {len(llama_docs)} Dokumente geladen")
            
            # Konvertiere zu unserem Document-Objekt
            documents = []
            for llama_doc in llama_docs:
                doc = Document(
                    content=llama_doc.text if hasattr(llama_doc, 'text') else llama_doc.page_content,
                    metadata=llama_doc.metadata
                )
                documents.append(doc)
            
            # Indexiere die Dokumente
            response = await rag_client.index_documents(
                documents=documents,
                collection_name=collection_name
            )
            
            if response.is_success:
                print(f"  -> Erfolgreich in Collection '{collection_name}' indexiert")
                successful_ingests += 1
            else:
                print(f"  -> Fehler bei der Indexierung: {response.error}")
                
        except Exception as e:
            print(f"  -> Fehler beim Laden der Datei {file_path.name}: {str(e)}")
    
    # Zeige die Anzahl der Dokumente in der Collection
    docs_response = await rag_client.get_documents(collection_name, limit=1000)
    if docs_response and 'documents' in docs_response:
        total_docs = len(docs_response['documents'])
        print(f"\nInsgesamt {total_docs} Dokumente in Collection '{collection_name}'")
        print(f"Erfolgreiche Ingests: {successful_ingests}/{min(10, len(test_files))}")
    else:
        print(f"Konnte Dokumente nicht abrufen von Collection '{collection_name}'")
    
    # Schließe den RAG-Client ordnungsgemäß
    await rag_client.shutdown()
    
    print("\nTest abgeschlossen!")


async def test_query_functionality():
    """Testet die Query-Funktionalität mit den indexierten Daten"""
    
    # Konfiguration für RAG-Client
    config = {
        "CHROMA_HOST": os.getenv("CHROMA_HOST", "127.0.0.1"),
        "CHROMA_PORT": int(os.getenv("CHROMA_PORT", 33801)),
        "CHROMA_IN_MEMORY": os.getenv("CHROMA_IN_MEMORY", "False").lower() == "true",
        "OLLAMA_HOST": os.getenv("OLLAMA_HOST", "127.0.0.1"),
        "OLLAMA_PORT": int(os.getenv("OLLAMA_PORT", 11434)),
        "DEFAULT_EMBEDDING_MODEL": os.getenv("DEFAULT_EMBEDDING_MODEL", "nomic-embed-text")
    }
    
    print("Erstelle RAG-Client für Query-Test...")
    rag_client = RAGClient(config)
    
    collection_name = "test_collection_extended"
    
    # Führe eine Test-Query durch
    query_text = "Steuerliche Beratung"
    print(f"\nFühre Query durch: '{query_text}' in Collection '{collection_name}'")
    
    response = await rag_client.query(
        query_text=query_text,
        collection_names=[collection_name],
        n_results=5
    )
    
    if response.is_success:
        results = response.data
        print(f"  -> {len(results)} Ergebnisse erhalten")
        
        for i, result in enumerate(results[:3]):  # Zeige die ersten 3 Ergebnisse
            print(f"    [{i+1}] Collection: {result.get('collection_name', 'N/A')}")
            print(f"         Score: {result.get('relevance_score', 'N/A')}")
            print(f"         Content (Auszug): {result.get('content', '')[:200]}...")
            print()
    else:
        print(f"  -> Query fehlgeschlagen: {response.error}")
    
    # Teste auch die Query-mit-Kontext-Funktionalität
    system_context = "Sie sind ein hilfreicher Assistent für steuerliche Fragen."
    print(f"Führe Query mit Kontext durch...")
    
    context_response = await rag_client.query_with_context(
        query_text="Welche Steuerformulare werden benötigt?",
        system_context=system_context,
        collection_names=[collection_name],
        n_results=3
    )
    
    if context_response and 'formatted_prompt' in context_response:
        print("  -> Query mit Kontext erfolgreich")
        print(f"     Kontext-Länge: {len(context_response['formatted_prompt'])} Zeichen")
    else:
        print("  -> Query mit Kontext fehlgeschlagen oder keine Antwort erhalten")
    
    # Schließe den RAG-Client ordnungsgemäß
    await rag_client.shutdown()
    
    print("Query-Test abgeschlossen!")


async def main():
    print("=== RAG Ingestion Test mit verschiedenen Dateitypen ===\n")
    
    print("Schritt 1: Teste Ingestion mit verschiedenen Dateitypen...")
    await test_ingestion_with_various_types()
    
    print("\n" + "="*60 + "\n")
    
    print("Schritt 2: Teste Query-Funktionalität...")
    await test_query_functionality()


if __name__ == "__main__":
    asyncio.run(main())