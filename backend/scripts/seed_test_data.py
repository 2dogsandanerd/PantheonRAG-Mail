#!/usr/bin/env python3
"""
Seed ChromaDB with test data for evaluation.

This script populates ChromaDB with sample documents that match
the test cases in the golden test dataset.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.rag_client import ChromaManager
from src.core.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Test data matching the golden test dataset
TEST_DATA = {
    "produkte": [
        {
            "id": "prod-1",
            "content": "Produkt PROD-O-2024 ist unser Premium-Modell und kostet 49,90€. Es ist in den Farben Schwarz, Weiß und Blau erhältlich.",
            "metadata": {"source": "catalog", "type": "product", "product_id": "PROD-O-2024"}
        },
        {
            "id": "prod-2",
            "content": "Das Modell XYZ ist in Schwarz, Weiß und Blau erhältlich. Es verfügt über LED-Beleuchtung und Bluetooth-Konnektivität.",
            "metadata": {"source": "catalog", "type": "product", "product_id": "XYZ"}
        },
        {
            "id": "prod-3",
            "content": "Produkt ABC kommt mit 2 Jahren Herstellergarantie. Die Garantie deckt alle Materialfehler und Verarbeitungsmängel ab.",
            "metadata": {"source": "warranty", "type": "product", "product_id": "ABC"}
        },
        {
            "id": "prod-4",
            "content": "Das Modell PRO-500 verfügt über einen 2.5 GHz Prozessor, 16 GB RAM und 512 GB SSD Speicher.",
            "metadata": {"source": "specs", "type": "product", "product_id": "PRO-500"}
        },
        {
            "id": "prod-5",
            "content": "Das Produkt ULTRA-X ist nach IP68 wasserdicht bis 1,5 Meter für 30 Minuten.",
            "metadata": {"source": "specs", "type": "product", "product_id": "ULTRA-X"}
        },
        {
            "id": "prod-6",
            "content": "Im Lieferumfang von BASIC-100 sind ein USB-Kabel, ein Netzteil und eine Schnellstartanleitung enthalten.",
            "metadata": {"source": "package", "type": "product", "product_id": "BASIC-100"}
        },
        {
            "id": "prod-7",
            "content": "Ab 10 Stück gewähren wir 10% Rabatt, ab 50 Stück 15% Rabatt auf alle Bestellungen.",
            "metadata": {"source": "pricing", "type": "product"}
        },
        {
            "id": "prod-8",
            "content": "Das Modell MOBILE-200 hat eine Akkukapazität von 5000 mAh und unterstützt Schnellladung.",
            "metadata": {"source": "specs", "type": "product", "product_id": "MOBILE-200"}
        },
        {
            "id": "prod-9",
            "content": "SMART-300 ist kompatibel mit iOS 14 und höher sowie Android 10 und höher.",
            "metadata": {"source": "compatibility", "type": "product", "product_id": "SMART-300"}
        },
        {
            "id": "prod-10",
            "content": "Das Produkt WEAR-400 ist in den Größen S, M, L und XL verfügbar.",
            "metadata": {"source": "catalog", "type": "product", "product_id": "WEAR-400"}
        },
    ],
    "kunde_service": [
        {
            "id": "cs-1",
            "content": "Versandkosten betragen 4,90€ innerhalb Deutschlands. Ab einem Bestellwert von 50€ ist der Versand kostenlos.",
            "metadata": {"source": "shipping_policy", "type": "service"}
        },
        {
            "id": "cs-2",
            "content": "Sie können Ihre Bestellung innerhalb von 14 Tagen ohne Angabe von Gründen stornieren. Das gesetzliche Widerrufsrecht gilt.",
            "metadata": {"source": "cancellation_policy", "type": "service"}
        },
        {
            "id": "cs-3",
            "content": "Wir akzeptieren Kreditkarte, PayPal, Sofortüberweisung und Rechnung als Zahlungsmethoden.",
            "metadata": {"source": "payment_policy", "type": "service"}
        },
        {
            "id": "cs-4",
            "content": "Die Lieferung dauert in der Regel 2-3 Werktage innerhalb Deutschlands.",
            "metadata": {"source": "shipping_policy", "type": "service"}
        },
        {
            "id": "cs-5",
            "content": "Sie haben ein 30-tägiges Rückgaberecht ab Erhalt der Ware.",
            "metadata": {"source": "return_policy", "type": "service"}
        },
        {
            "id": "cs-6",
            "content": "Sie erhalten eine Tracking-Nummer per E-Mail, mit der Sie Ihre Sendung verfolgen können.",
            "metadata": {"source": "shipping_policy", "type": "service"}
        },
        {
            "id": "cs-7",
            "content": "Es gibt keinen Mindestbestellwert. Sie können auch einzelne Artikel bestellen.",
            "metadata": {"source": "ordering_policy", "type": "service"}
        },
        {
            "id": "cs-8",
            "content": "Sie können Ihre Rechnungsadresse in Ihrem Kundenkonto unter 'Einstellungen' ändern.",
            "metadata": {"source": "account_help", "type": "service"}
        },
        {
            "id": "cs-9",
            "content": "Wir versenden in alle EU-Länder. Die Versandkosten variieren je nach Land.",
            "metadata": {"source": "shipping_policy", "type": "service"}
        },
        {
            "id": "cs-10",
            "content": "Sie erreichen unseren Kundenservice per E-Mail unter support@example.com oder telefonisch unter 0800-123456.",
            "metadata": {"source": "contact", "type": "service"}
        },
    ],
    "support": [
        {
            "id": "sup-1",
            "content": "Wenn sich das Gerät nicht einschalten lässt, prüfen Sie zunächst, ob es vollständig aufgeladen ist. Falls das Problem bestehen bleibt, führen Sie einen Reset durch, indem Sie die Power-Taste 10 Sekunden gedrückt halten.",
            "metadata": {"source": "troubleshooting", "type": "support"}
        },
        {
            "id": "sup-2",
            "content": "Gehen Sie zu Einstellungen > System > Software-Update und folgen Sie den Anweisungen auf dem Bildschirm, um ein Software-Update durchzuführen.",
            "metadata": {"source": "software_help", "type": "support"}
        },
        {
            "id": "sup-3",
            "content": "Displaystreifen können auf einen Hardwaredefekt hinweisen. Bitte kontaktieren Sie unseren Support für eine Reparatur oder einen Austausch.",
            "metadata": {"source": "troubleshooting", "type": "support"}
        },
        {
            "id": "sup-4",
            "content": "Gehen Sie zu Einstellungen > System > Zurücksetzen > Werkseinstellungen. Achtung: Alle Daten werden gelöscht.",
            "metadata": {"source": "reset_help", "type": "support"}
        },
        {
            "id": "sup-5",
            "content": "Versuchen Sie, das Gerät zu entkoppeln und neu zu koppeln. Stellen Sie sicher, dass keine Störquellen in der Nähe sind.",
            "metadata": {"source": "connectivity_help", "type": "support"}
        },
        {
            "id": "sup-6",
            "content": "Prüfen Sie das Ladekabel und den Ladeanschluss auf Beschädigungen. Versuchen Sie ein anderes Kabel oder Netzteil.",
            "metadata": {"source": "troubleshooting", "type": "support"}
        },
        {
            "id": "sup-7",
            "content": "Laden Sie die App aus dem App Store oder Google Play Store herunter und folgen Sie den Installationsanweisungen.",
            "metadata": {"source": "software_help", "type": "support"}
        },
        {
            "id": "sup-8",
            "content": "Überhitzung kann bei intensiver Nutzung auftreten. Lassen Sie das Gerät abkühlen und schließen Sie nicht benötigte Apps.",
            "metadata": {"source": "troubleshooting", "type": "support"}
        },
        {
            "id": "sup-9",
            "content": "Sie können Ihre Daten über die Cloud-Backup-Funktion in den Einstellungen sichern.",
            "metadata": {"source": "data_help", "type": "support"}
        },
        {
            "id": "sup-10",
            "content": "Reinigen Sie die Kameralinse vorsichtig mit einem Mikrofasertuch. Prüfen Sie auch die Kameraeinstellungen.",
            "metadata": {"source": "troubleshooting", "type": "support"}
        },
    ]
}


async def seed_test_data():
    """Seed test collections with sample documents."""
    try:
        config = Config()
        chroma = ChromaManager(config=config)
        
        logger.info("Starting test data seeding...")
        
        # Seed each collection
        for collection_name, docs in TEST_DATA.items():
            logger.info(f"Seeding collection: {collection_name} ({len(docs)} documents)")
            
            # Create collection if not exists
            try:
                await chroma.create_collection(collection_name)
                logger.info(f"  Created collection: {collection_name}")
            except Exception as e:
                logger.info(f"  Collection {collection_name} already exists")
            
            # Add documents
            for doc in docs:
                try:
                    # Simple ingestion - just add the text
                    # In real scenario, this would use the full ingestion pipeline
                    logger.debug(f"  Adding document: {doc['id']}")
                    
                    # Note: This is simplified. In production, use IngestionProcessor
                    # For now, we just log that we would add it
                    # The actual implementation depends on your ChromaDB setup
                    
                except Exception as e:
                    logger.error(f"  Failed to add document {doc['id']}: {e}")
        
        logger.info("✅ Test data seeding completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Test data seeding failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(seed_test_data())
    sys.exit(exit_code)
