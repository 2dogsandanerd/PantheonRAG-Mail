"""
Golden Test Dataset for RAG Evaluation.

This module contains curated test cases with ground truth answers for
automated quality assurance of the RAG system.

Test cases are organized by:
- Domain (PRODUKTE, KUNDE_SERVICE, SUPPORT, etc.)
- Category (pricing, shipping, troubleshooting, etc.)
- Difficulty (easy, medium, hard)
"""

from typing import List, Dict, Any
from pydantic import BaseModel


class RAGTestCase(BaseModel):
    """Single RAG test case with ground truth."""
    
    id: str
    query: str
    expected_domain: str
    ground_truth: str
    required_context_keywords: List[str]
    max_hallucination_score: float = 0.1  # 1 - faithfulness
    min_relevancy_score: float = 0.7
    collections: List[str]
    metadata: Dict[str, Any] = {}


# ============================================================================
# PRODUCT TESTS
# ============================================================================

PRODUCT_TESTS = [
    RAGTestCase(
        id="PROD-001",
        query="Was kostet Produkt PROD-O-2024?",
        expected_domain="PRODUKTE",
        ground_truth="Das Produkt PROD-O-2024 kostet 49,90€.",
        required_context_keywords=["PROD-O-2024", "49,90", "€"],
        collections=["produkte"],
        metadata={"category": "pricing", "difficulty": "easy"}
    ),
    RAGTestCase(
        id="PROD-002",
        query="Welche Farben gibt es für das Modell XYZ?",
        expected_domain="PRODUKTE",
        ground_truth="Das Modell XYZ ist in Schwarz, Weiß und Blau erhältlich.",
        required_context_keywords=["XYZ", "Farben", "Schwarz", "Weiß", "Blau"],
        collections=["produkte"],
        metadata={"category": "product_details", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="PROD-003",
        query="Gibt es eine Garantie für Produkt ABC?",
        expected_domain="PRODUKTE",
        ground_truth="Produkt ABC hat 2 Jahre Herstellergarantie.",
        required_context_keywords=["ABC", "Garantie", "2 Jahre"],
        collections=["produkte"],
        metadata={"category": "warranty", "difficulty": "easy"}
    ),
    RAGTestCase(
        id="PROD-004",
        query="Welche technischen Spezifikationen hat das Modell PRO-500?",
        expected_domain="PRODUKTE",
        ground_truth="Das Modell PRO-500 verfügt über einen 2.5 GHz Prozessor, 16 GB RAM und 512 GB SSD.",
        required_context_keywords=["PRO-500", "2.5 GHz", "16 GB", "512 GB"],
        collections=["produkte"],
        metadata={"category": "specifications", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="PROD-005",
        query="Ist das Produkt ULTRA-X wasserdicht?",
        expected_domain="PRODUKTE",
        ground_truth="Ja, das Produkt ULTRA-X ist nach IP68 wasserdicht bis 1,5 Meter für 30 Minuten.",
        required_context_keywords=["ULTRA-X", "wasserdicht", "IP68"],
        collections=["produkte"],
        metadata={"category": "features", "difficulty": "easy"}
    ),
    RAGTestCase(
        id="PROD-006",
        query="Welches Zubehör ist im Lieferumfang von Produkt BASIC-100 enthalten?",
        expected_domain="PRODUKTE",
        ground_truth="Im Lieferumfang von BASIC-100 sind ein USB-Kabel, ein Netzteil und eine Schnellstartanleitung enthalten.",
        required_context_keywords=["BASIC-100", "USB-Kabel", "Netzteil", "Anleitung"],
        collections=["produkte"],
        metadata={"category": "package_contents", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="PROD-007",
        query="Gibt es Rabatte für Großbestellungen?",
        expected_domain="PRODUKTE",
        ground_truth="Ja, ab 10 Stück gewähren wir 10% Rabatt, ab 50 Stück 15% Rabatt.",
        required_context_keywords=["Rabatt", "10 Stück", "10%", "50 Stück", "15%"],
        collections=["produkte"],
        metadata={"category": "pricing", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="PROD-008",
        query="Welche Akkukapazität hat das Modell MOBILE-200?",
        expected_domain="PRODUKTE",
        ground_truth="Das Modell MOBILE-200 hat eine Akkukapazität von 5000 mAh.",
        required_context_keywords=["MOBILE-200", "5000 mAh", "Akku"],
        collections=["produkte"],
        metadata={"category": "specifications", "difficulty": "easy"}
    ),
    RAGTestCase(
        id="PROD-009",
        query="Ist das Produkt SMART-300 mit iOS kompatibel?",
        expected_domain="PRODUKTE",
        ground_truth="Ja, SMART-300 ist kompatibel mit iOS 14 und höher.",
        required_context_keywords=["SMART-300", "iOS", "kompatibel"],
        collections=["produkte"],
        metadata={"category": "compatibility", "difficulty": "easy"}
    ),
    RAGTestCase(
        id="PROD-010",
        query="Welche Größen sind für das Produkt WEAR-400 verfügbar?",
        expected_domain="PRODUKTE",
        ground_truth="Das Produkt WEAR-400 ist in den Größen S, M, L und XL verfügbar.",
        required_context_keywords=["WEAR-400", "S", "M", "L", "XL"],
        collections=["produkte"],
        metadata={"category": "product_details", "difficulty": "easy"}
    ),
]


# ============================================================================
# CUSTOMER SERVICE TESTS
# ============================================================================

CUSTOMER_TESTS = [
    RAGTestCase(
        id="CUST-001",
        query="Wie hoch sind die Versandkosten?",
        expected_domain="KUNDE_SERVICE",
        ground_truth="Die Versandkosten betragen 4,90€ innerhalb Deutschlands. Ab 50€ Bestellwert ist der Versand kostenlos.",
        required_context_keywords=["Versandkosten", "4,90", "50€", "kostenlos"],
        collections=["kunde_service"],
        metadata={"category": "shipping", "difficulty": "easy"}
    ),
    RAGTestCase(
        id="CUST-002",
        query="Wie kann ich meine Bestellung stornieren?",
        expected_domain="KUNDE_SERVICE",
        ground_truth="Sie können Ihre Bestellung innerhalb von 14 Tagen ohne Angabe von Gründen stornieren.",
        required_context_keywords=["stornieren", "14 Tage", "Widerrufsrecht"],
        collections=["kunde_service"],
        metadata={"category": "cancellation", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="CUST-003",
        query="Welche Zahlungsmethoden werden akzeptiert?",
        expected_domain="KUNDE_SERVICE",
        ground_truth="Wir akzeptieren Kreditkarte, PayPal, Sofortüberweisung und Rechnung.",
        required_context_keywords=["Kreditkarte", "PayPal", "Sofortüberweisung", "Rechnung"],
        collections=["kunde_service"],
        metadata={"category": "payment", "difficulty": "easy"}
    ),
    RAGTestCase(
        id="CUST-004",
        query="Wie lange dauert die Lieferung?",
        expected_domain="KUNDE_SERVICE",
        ground_truth="Die Lieferung dauert in der Regel 2-3 Werktage innerhalb Deutschlands.",
        required_context_keywords=["Lieferung", "2-3 Werktage", "Deutschland"],
        collections=["kunde_service"],
        metadata={"category": "shipping", "difficulty": "easy"}
    ),
    RAGTestCase(
        id="CUST-005",
        query="Kann ich meine Bestellung zurückgeben?",
        expected_domain="KUNDE_SERVICE",
        ground_truth="Ja, Sie haben ein 30-tägiges Rückgaberecht ab Erhalt der Ware.",
        required_context_keywords=["Rückgabe", "30 Tage", "Rückgaberecht"],
        collections=["kunde_service"],
        metadata={"category": "returns", "difficulty": "easy"}
    ),
    RAGTestCase(
        id="CUST-006",
        query="Wie kann ich den Bestellstatus verfolgen?",
        expected_domain="KUNDE_SERVICE",
        ground_truth="Sie erhalten eine Tracking-Nummer per E-Mail, mit der Sie Ihre Sendung verfolgen können.",
        required_context_keywords=["Tracking", "E-Mail", "verfolgen"],
        collections=["kunde_service"],
        metadata={"category": "shipping", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="CUST-007",
        query="Gibt es einen Mindestbestellwert?",
        expected_domain="KUNDE_SERVICE",
        ground_truth="Nein, es gibt keinen Mindestbestellwert.",
        required_context_keywords=["Mindestbestellwert", "kein"],
        collections=["kunde_service"],
        metadata={"category": "ordering", "difficulty": "easy"}
    ),
    RAGTestCase(
        id="CUST-008",
        query="Wie kann ich meine Rechnungsadresse ändern?",
        expected_domain="KUNDE_SERVICE",
        ground_truth="Sie können Ihre Rechnungsadresse in Ihrem Kundenkonto unter 'Einstellungen' ändern.",
        required_context_keywords=["Rechnungsadresse", "Kundenkonto", "Einstellungen"],
        collections=["kunde_service"],
        metadata={"category": "account", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="CUST-009",
        query="Wird international versendet?",
        expected_domain="KUNDE_SERVICE",
        ground_truth="Ja, wir versenden in alle EU-Länder. Die Versandkosten variieren je nach Land.",
        required_context_keywords=["international", "EU", "Versandkosten"],
        collections=["kunde_service"],
        metadata={"category": "shipping", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="CUST-010",
        query="Wie kontaktiere ich den Kundenservice?",
        expected_domain="KUNDE_SERVICE",
        ground_truth="Sie erreichen unseren Kundenservice per E-Mail unter support@example.com oder telefonisch unter 0800-123456.",
        required_context_keywords=["Kundenservice", "E-Mail", "Telefon"],
        collections=["kunde_service"],
        metadata={"category": "contact", "difficulty": "easy"}
    ),
]


# ============================================================================
# SUPPORT TESTS
# ============================================================================

SUPPORT_TESTS = [
    RAGTestCase(
        id="SUPP-001",
        query="Produkt lässt sich nicht einschalten",
        expected_domain="SUPPORT",
        ground_truth="Bitte prüfen Sie zunächst, ob das Gerät vollständig aufgeladen ist. Falls das Problem bestehen bleibt, führen Sie einen Reset durch.",
        required_context_keywords=["einschalten", "aufgeladen", "Reset"],
        collections=["support"],
        metadata={"category": "troubleshooting", "difficulty": "hard"}
    ),
    RAGTestCase(
        id="SUPP-002",
        query="Wie führe ich ein Software-Update durch?",
        expected_domain="SUPPORT",
        ground_truth="Gehen Sie zu Einstellungen > System > Software-Update und folgen Sie den Anweisungen auf dem Bildschirm.",
        required_context_keywords=["Software-Update", "Einstellungen", "System"],
        collections=["support"],
        metadata={"category": "software", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="SUPP-003",
        query="Das Display zeigt Streifen an",
        expected_domain="SUPPORT",
        ground_truth="Displaystreifen können auf einen Hardwaredefekt hinweisen. Bitte kontaktieren Sie unseren Support für eine Reparatur oder einen Austausch.",
        required_context_keywords=["Display", "Streifen", "Hardwaredefekt", "Support"],
        collections=["support"],
        metadata={"category": "troubleshooting", "difficulty": "hard"}
    ),
    RAGTestCase(
        id="SUPP-004",
        query="Wie setze ich das Gerät auf Werkseinstellungen zurück?",
        expected_domain="SUPPORT",
        ground_truth="Gehen Sie zu Einstellungen > System > Zurücksetzen > Werkseinstellungen. Achtung: Alle Daten werden gelöscht.",
        required_context_keywords=["Werkseinstellungen", "zurücksetzen", "Daten gelöscht"],
        collections=["support"],
        metadata={"category": "reset", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="SUPP-005",
        query="Die Bluetooth-Verbindung bricht ständig ab",
        expected_domain="SUPPORT",
        ground_truth="Versuchen Sie, das Gerät zu entkoppeln und neu zu koppeln. Stellen Sie sicher, dass keine Störquellen in der Nähe sind.",
        required_context_keywords=["Bluetooth", "entkoppeln", "neu koppeln"],
        collections=["support"],
        metadata={"category": "connectivity", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="SUPP-006",
        query="Der Akku lädt nicht",
        expected_domain="SUPPORT",
        ground_truth="Prüfen Sie das Ladekabel und den Ladeanschluss auf Beschädigungen. Versuchen Sie ein anderes Kabel oder Netzteil.",
        required_context_keywords=["Akku", "lädt nicht", "Ladekabel", "Netzteil"],
        collections=["support"],
        metadata={"category": "troubleshooting", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="SUPP-007",
        query="Wie installiere ich die App?",
        expected_domain="SUPPORT",
        ground_truth="Laden Sie die App aus dem App Store oder Google Play Store herunter und folgen Sie den Installationsanweisungen.",
        required_context_keywords=["App", "App Store", "Google Play", "Installation"],
        collections=["support"],
        metadata={"category": "software", "difficulty": "easy"}
    ),
    RAGTestCase(
        id="SUPP-008",
        query="Das Gerät wird sehr heiß",
        expected_domain="SUPPORT",
        ground_truth="Überhitzung kann bei intensiver Nutzung auftreten. Lassen Sie das Gerät abkühlen und schließen Sie nicht benötigte Apps.",
        required_context_keywords=["heiß", "Überhitzung", "abkühlen"],
        collections=["support"],
        metadata={"category": "troubleshooting", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="SUPP-009",
        query="Wie kann ich meine Daten sichern?",
        expected_domain="SUPPORT",
        ground_truth="Sie können Ihre Daten über die Cloud-Backup-Funktion in den Einstellungen sichern.",
        required_context_keywords=["Daten sichern", "Cloud", "Backup", "Einstellungen"],
        collections=["support"],
        metadata={"category": "data", "difficulty": "medium"}
    ),
    RAGTestCase(
        id="SUPP-010",
        query="Die Kamera macht unscharfe Bilder",
        expected_domain="SUPPORT",
        ground_truth="Reinigen Sie die Kameralinse vorsichtig mit einem Mikrofasertuch. Prüfen Sie auch die Kameraeinstellungen.",
        required_context_keywords=["Kamera", "unscharf", "Linse", "reinigen"],
        collections=["support"],
        metadata={"category": "troubleshooting", "difficulty": "medium"}
    ),
]


# ============================================================================
# COMBINED DATASET
# ============================================================================

ALL_TESTS = PRODUCT_TESTS + CUSTOMER_TESTS + SUPPORT_TESTS


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_tests_by_category(category: str) -> List[RAGTestCase]:
    """Get all tests for a specific category."""
    return [t for t in ALL_TESTS if t.metadata.get("category") == category]


def get_tests_by_domain(domain: str) -> List[RAGTestCase]:
    """Get all tests for a specific domain."""
    return [t for t in ALL_TESTS if t.expected_domain == domain]


def get_tests_by_difficulty(difficulty: str) -> List[RAGTestCase]:
    """Get tests by difficulty level."""
    return [t for t in ALL_TESTS if t.metadata.get("difficulty") == difficulty]


def get_test_by_id(test_id: str) -> Optional[RAGTestCase]:
    """Get a specific test by ID."""
    for test in ALL_TESTS:
        if test.id == test_id:
            return test
    return None


def get_test_statistics() -> Dict[str, Any]:
    """Get statistics about the test dataset."""
    stats = {
        "total_tests": len(ALL_TESTS),
        "by_domain": {},
        "by_category": {},
        "by_difficulty": {}
    }
    
    for test in ALL_TESTS:
        # Domain stats
        domain = test.expected_domain
        stats["by_domain"][domain] = stats["by_domain"].get(domain, 0) + 1
        
        # Category stats
        category = test.metadata.get("category", "unknown")
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        
        # Difficulty stats
        difficulty = test.metadata.get("difficulty", "unknown")
        stats["by_difficulty"][difficulty] = stats["by_difficulty"].get(difficulty, 0) + 1
    
    return stats
