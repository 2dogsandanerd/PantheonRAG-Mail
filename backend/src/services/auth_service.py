"""
auth_service.py — Bridge-Modul für Auth-Funktionen.

Leitet alle Aufrufe an die echte JWT-Implementierung in src.core.auth weiter.
Dadurch müssen bestehende Imports nicht einzeln geändert werden.

ACHTUNG: Der alte Dummy-User ist ENTFERNT. Diese Datei ist jetzt ein reines
Weiterleitungs-Modul zur Rückwärts-Kompatibilität.
"""

# Re-export der echten Auth-Funktionen aus core.auth
from src.core.auth import (
    get_current_user,
    get_current_active_user,
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]
