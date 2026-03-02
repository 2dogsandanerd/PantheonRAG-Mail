"""
upload_security.py — Upload Security Utilities für PantheonMail Backend.

Shared validation logic für File-Uploads.
Defense in depth: Extension-Whitelist + Magic-Byte-Check + Größenlimit + Isolated Temp Dir.

Hinweis: python-magic muss installiert sein (libmagic1 System-Dependency).
Falls nicht verfügbar, fällt die Validierung auf Extension-only zurück (mit Warning).
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from fastapi import HTTPException
from loguru import logger

# Maximale Dateigröße: 100 MB
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024

# Erlaubte Dateitypen: Extension → erlaubte MIME-Typen
ALLOWED_FILE_TYPES: dict[str, list[str]] = {
    ".pdf":  ["application/pdf"],
    ".txt":  ["text/plain"],
    ".md":   ["text/plain", "text/markdown"],
    ".docx": [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",  # docx ist ein ZIP
    ],
    ".xlsx": [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/zip",
    ],
    ".pptx": [
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/zip",
    ],
    ".csv":  ["text/csv", "text/plain"],
    ".json": ["application/json", "text/plain"],
    ".html": ["text/html"],
    ".htm":  ["text/html"],
    ".xml":  ["application/xml", "text/xml", "text/plain"],
}

# Versuche python-magic zu laden — graceful degradation wenn nicht verfügbar
try:
    import magic as _magic
    _MAGIC_AVAILABLE = True
except ImportError:
    _MAGIC_AVAILABLE = False
    logger.warning(
        "python-magic nicht installiert. Magic-Byte-Validierung deaktiviert. "
        "Nur Extension-Whitelist wird verwendet. "
        "Installieren mit: pip install python-magic"
    )


def validate_file_extension(filename: str) -> str:
    """
    Prüft ob die Datei-Extension auf der Whitelist steht.
    
    Returns: Extension (z.B. '.pdf')
    Raises: HTTPException(400) wenn nicht erlaubt
    """
    ext = Path(filename).suffix.lower()
    if not ext:
        raise HTTPException(
            status_code=400,
            detail="Datei ohne Extension wird nicht akzeptiert."
        )
    if ext not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Dateityp '{ext}' ist nicht erlaubt. "
                f"Erlaubte Typen: {sorted(ALLOWED_FILE_TYPES.keys())}"
            )
        )
    return ext


def validate_magic_bytes(filename: str, content: bytes) -> str:
    """
    Prüft den tatsächlichen MIME-Typ via Magic Bytes.
    Fällt graceful zurück wenn python-magic nicht verfügbar.
    
    Returns: Erkannter MIME-Typ
    Raises: HTTPException(400) bei Typ-Mismatch
    """
    ext = validate_file_extension(filename)
    
    if not _MAGIC_AVAILABLE:
        logger.debug(f"Magic-Byte-Check übersprungen (python-magic nicht verfügbar): {filename}")
        return "unknown"
    
    try:
        detected_mime = _magic.from_buffer(content[:8192], mime=True)
    except Exception as e:
        logger.warning(f"Magic-Byte-Erkennung fehlgeschlagen für {filename}: {e}")
        # Bei Fehler erlauben wir den Upload mit Warnung (nicht blockieren)
        return "detection_failed"
    
    allowed_mimes = ALLOWED_FILE_TYPES.get(ext, [])
    if detected_mime not in allowed_mimes:
        logger.warning(
            f"Magic-Byte-Mismatch: Datei='{filename}', "
            f"Extension='{ext}', Erkannt='{detected_mime}', "
            f"Erwartet={allowed_mimes}"
        )
        raise HTTPException(
            status_code=400,
            detail=(
                f"Datei-Inhalt ('{detected_mime}') entspricht nicht der Extension '{ext}'. "
                "Upload abgelehnt."
            )
        )
    
    return detected_mime


def validate_file_size(filename: str, size_bytes: int) -> None:
    """
    Prüft ob die Dateigröße das Limit nicht überschreitet.
    
    Raises: HTTPException(413) wenn zu groß
    """
    if size_bytes > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES // 1024 // 1024
        raise HTTPException(
            status_code=413,
            detail=(
                f"Datei '{filename}' ist zu groß ({size_bytes // 1024 // 1024} MB). "
                f"Maximum: {max_mb} MB"
            )
        )


def create_secure_temp_dir(prefix: str = "pantheon_upload_") -> str:
    """
    Erstellt ein isoliertes Temp-Verzeichnis für sicheres Datei-Processing.
    
    Der Aufrufer ist für das Cleanup verantwortlich (try/finally mit cleanup_temp_dir).
    
    Returns: Pfad zum Temp-Verzeichnis
    """
    return tempfile.mkdtemp(prefix=prefix)


def cleanup_temp_dir(temp_dir: Optional[str]) -> None:
    """
    Löscht ein Temp-Verzeichnis sicher. Wirft nie eine Exception.
    """
    if not temp_dir:
        return
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.debug(f"Temp-Verzeichnis bereinigt: {temp_dir}")
    except Exception as e:
        logger.error(f"Fehler beim Bereinigen von Temp-Verzeichnis {temp_dir}: {e}")


def get_safe_filename(filename: str) -> str:
    """
    Gibt einen sicheren Dateinamen zurück (nur Basename, kein Path-Traversal).
    """
    return os.path.basename(filename)
