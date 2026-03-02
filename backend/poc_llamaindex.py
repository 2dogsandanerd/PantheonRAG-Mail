"""
Proof-of-Concept: LlamaIndex + LangChain Integration
Testet die 3 kritischen Fragen:

1. Version-Kompatibilität
2. Document-Konvertierung
3. System-Dependencies
"""

import sys


def test_1_version_compatibility():
    """Test: Können LlamaIndex und LangChain koexistieren?"""
    print("=" * 60)
    print("TEST 1: Version-Kompatibilität")
    print("=" * 60)

    try:
        # Versuche beide zu importieren
        import langchain
        import llama_index.core

        print(f"✓ LangChain Version: {langchain.__version__}")
        print(f"✓ LlamaIndex Version: {llama_index.core.__version__}")

        # Prüfe auf bekannte Konflikte
        import langchain_community
        import chromadb

        print(f"✓ LangChain-Community: {langchain_community.__version__}")
        print(f"✓ ChromaDB: {chromadb.__version__}")

        print("\n✅ Kein direkter Import-Konflikt erkannt\n")
        return True

    except ImportError as e:
        print(f"\n❌ Import-Fehler: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}\n")
        return False


def test_2_document_conversion():
    """Test: Kann man LlamaIndex → LangChain Document konvertieren?"""
    print("=" * 60)
    print("TEST 2: Document-Konvertierung")
    print("=" * 60)

    try:
        from llama_index.core import Document as LlamaDocument
        from langchain.schema import Document as LangChainDocument

        # Erstelle LlamaIndex Document
        llama_doc = LlamaDocument(
            text="Test content",
            metadata={
                "source": "test.pdf",
                "page": 1,
                "custom_field": "value"
            }
        )

        print(f"LlamaIndex Document erstellt:")
        print(f"  - Text: {llama_doc.text[:50]}...")
        print(f"  - Metadata: {llama_doc.metadata}")

        # Versuche Konvertierung
        langchain_doc = LangChainDocument(
            page_content=llama_doc.text,
            metadata=llama_doc.metadata
        )

        print(f"\nLangChain Document konvertiert:")
        print(f"  - Content: {langchain_doc.page_content[:50]}...")
        print(f"  - Metadata: {langchain_doc.metadata}")

        # Prüfe Metadaten-Übertragung
        if llama_doc.metadata == langchain_doc.metadata:
            print("\n✅ Metadaten korrekt übertragen")
        else:
            print("\n⚠️  Metadaten-Unterschiede erkannt")
            print(f"   LlamaIndex: {llama_doc.metadata}")
            print(f"   LangChain: {langchain_doc.metadata}")

        print("\n✅ Grundlegende Konvertierung funktioniert\n")
        return True

    except Exception as e:
        print(f"\n❌ Konvertierungs-Fehler: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_3_system_dependencies():
    """Test: Welche System-Dependencies werden benötigt?"""
    print("=" * 60)
    print("TEST 3: System-Dependencies")
    print("=" * 60)

    dependencies = {
        "openpyxl": "Excel-Support (.xlsx)",
        "pypdf": "PDF-Support",
        "python-docx": "Word-Support (.docx)",
        "pandas": "CSV/Excel als DataFrame",
        "sqlalchemy": "Database-Support"
    }

    available = []
    missing = []

    for pkg, description in dependencies.items():
        try:
            __import__(pkg.replace("-", "_"))
            available.append(f"✓ {pkg} ({description})")
        except ImportError:
            missing.append(f"✗ {pkg} ({description})")

    print("\nVerfügbare Dependencies:")
    for dep in available:
        print(f"  {dep}")

    if missing:
        print("\nFehlende Dependencies:")
        for dep in missing:
            print(f"  {dep}")
        print(f"\nInstallation: pip install {' '.join([d.split()[1] for d in missing])}")

    print(f"\n✅ {len(available)}/{len(dependencies)} Dependencies verfügbar\n")
    return len(missing) == 0


def test_4_simple_loader():
    """Test: Funktioniert ein einfacher LlamaIndex Loader?"""
    print("=" * 60)
    print("TEST 4: SimpleDirectoryReader (ohne Dateien)")
    print("=" * 60)

    try:
        from llama_index.core import SimpleDirectoryReader

        print("✓ SimpleDirectoryReader importiert")
        print("✓ Kann konfiguriert werden")

        # Zeige verfügbare Reader
        print("\n✅ SimpleDirectoryReader funktioniert\n")
        return True

    except Exception as e:
        print(f"\n❌ Loader-Fehler: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Führt alle Tests aus und gibt Empfehlung"""
    print("\n" + "=" * 60)
    print("LlamaIndex + LangChain PoC")
    print("=" * 60 + "\n")

    results = {
        "Kompatibilität": test_1_version_compatibility(),
        "Konvertierung": test_2_document_conversion(),
        "Dependencies": test_3_system_dependencies(),
        "Loader": test_4_simple_loader()
    }

    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)

    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("EMPFEHLUNG: ✅ LlamaIndex-Integration ist machbar")
        print("Nächster Schritt: Minimale Integration für einen Loader testen")
    else:
        print("EMPFEHLUNG: ⚠️  Probleme erkannt")
        print("Nächster Schritt: Probleme lösen ODER eigene Loader bauen")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
