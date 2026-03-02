"""
Standalone Entry-Point für PyInstaller

Startet Uvicorn-Server ohne CLI-Arguments.
In PyInstaller-Binary wird dieser Einstiegspunkt verwendet.
"""

import sys
import os
import multiprocessing

# Fix für PyInstaller: Multiprocessing unter Windows
if __name__ == '__main__':
    multiprocessing.freeze_support()

# Fix für PyInstaller: Working Directory setzen
if getattr(sys, 'frozen', False):
    # PyInstaller-Modus: sys._MEIPASS zeigt auf temporäres Extraktions-Verzeichnis
    application_path = sys._MEIPASS

    # .env aus App-Daten laden (falls vorhanden)
    # Electron setzt DOTENV_PATH Environment-Variable
    dotenv_path = os.environ.get('DOTENV_PATH')
    if dotenv_path and os.path.exists(dotenv_path):
        from dotenv import load_dotenv
        load_dotenv(dotenv_path)
        print(f"[Standalone] Loaded .env from: {dotenv_path}")
else:
    # Normal-Modus (Development)
    application_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(application_path)

print(f"[Standalone] Working directory: {os.getcwd()}")
print(f"[Standalone] Python version: {sys.version}")
print(f"[Standalone] Frozen: {getattr(sys, 'frozen', False)}")

# Uvicorn-Server starten
import uvicorn
from src.main import app

if __name__ == "__main__":
    print("[Standalone] Starting FastAPI server...")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=33800,
        log_level="info",
        # Wichtig: access_log=False für bessere Performance
        access_log=False
    )
