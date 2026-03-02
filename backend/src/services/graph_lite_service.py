# backend/src/services/graph_lite_service.py
import sqlite3
import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class GraphLiteService:
    """
    Fiat Strategy: Graph-Lite.
    Uses SQLite to store entity-relation facts instead of a full Neo4j graph.
    Optimized for local performance and metadata-based RAG enrichment.
    """

    def __init__(self, db_path: str = "data/graph_lite.db"):
        self.db_path = db_path
        # Ensure data directory exists
        Path(os.path.dirname(self.db_path)).mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite tables for entities and relations."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Entities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    metadata TEXT,
                    UNIQUE(name, type)
                )
            """)
            # Relations table (Simple Triplets: Subject -> Predicate -> Object)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER NOT NULL,
                    predicate TEXT NOT NULL,
                    object_id INTEGER NOT NULL,
                    confidence FLOAT DEFAULT 1.0,
                    FOREIGN KEY (subject_id) REFERENCES entities(id),
                    FOREIGN KEY (object_id) REFERENCES entities(id)
                )
            """)
            conn.commit()
            logger.info(f"Graph-Lite Database initialized at {self.db_path}")

    def add_fact(self, subject: str, subject_type: str, predicate: str, obj: str, obj_type: str, confidence: float = 1.0):
        """Add a factual relation between two entities."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get or create subject
            cursor.execute("INSERT OR IGNORE INTO entities (name, type) VALUES (?, ?)", (subject, subject_type))
            cursor.execute("SELECT id FROM entities WHERE name = ? AND type = ?", (subject, subject_type))
            subject_id = cursor.fetchone()[0]
            
            # Get or create object
            cursor.execute("INSERT OR IGNORE INTO entities (name, type) VALUES (?, ?)", (obj, obj_type))
            cursor.execute("SELECT id FROM entities WHERE name = ? AND type = ?", (obj, obj_type))
            object_id = cursor.fetchone()[0]
            
            # Add relation
            cursor.execute("""
                INSERT INTO relations (subject_id, predicate, object_id, confidence)
                VALUES (?, ?, ?, ?)
            """, (subject_id, predicate, object_id, confidence))
            conn.commit()
            logger.info(f"Fact added: {subject} --({predicate})--> {obj}")

    def query_facts(self, entity_name: str) -> List[Dict[str, Any]]:
        """Retrieve all known facts related to an entity."""
        facts = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = """
                SELECT e1.name, r.predicate, e2.name, r.confidence
                FROM relations r
                JOIN entities e1 ON r.subject_id = e1.id
                JOIN entities e2 ON r.object_id = e2.id
                WHERE e1.name LIKE ? OR e2.name LIKE ?
            """
            cursor.execute(query, (f"%{entity_name}%", f"%{entity_name}%"))
            for row in cursor.fetchall():
                facts.append({
                    "subject": row[0],
                    "predicate": row[1],
                    "object": row[2],
                    "confidence": row[3]
                })
        return facts

    def get_context_for_rag(self, text: str) -> str:
        """
        Scan text for known entities and return a string of relevant facts.
        This can be injected into the LLM prompt.
        """
        # Very simple entity extraction for MVP: keyword matching
        known_entities = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM entities")
            entities = [row[0] for row in cursor.fetchall()]
            
            for entity in entities:
                if entity.lower() in text.lower():
                    known_entities.append(entity)
        
        if not known_entities:
            return ""
            
        all_facts = []
        for entity in known_entities:
            facts = self.query_facts(entity)
            for f in facts:
                all_facts.append(f"{f['subject']} {f['predicate']} {f['object']}")
                
        if not all_facts:
            return ""
            
        context = "\n[Graph-Lite Facts]:\n- " + "\n- ".join(list(set(all_facts)))
        return context

# Singleton for easy access
graph_lite = GraphLiteService()
