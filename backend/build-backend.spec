# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File für Mail Assistant Backend

Erstellt eine standalone .exe, die FastAPI-Server enthält.
Keine Python-Installation beim User erforderlich.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Projekt-Root ermitteln
backend_dir = os.path.abspath(SPECPATH)
project_root = os.path.dirname(backend_dir)

# Alle versteckten Imports sammeln (wichtig für dynamische Imports)
hidden_imports = [
    # Uvicorn
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',

    # FastAPI
    'fastapi',
    'fastapi.routing',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'starlette.middleware',
    'starlette.middleware.cors',

    # SQLAlchemy
    'sqlalchemy',
    'sqlalchemy.ext.baked',
    'sqlalchemy.sql.default_comparator',

    # Pydantic
    'pydantic',
    'pydantic.types',
    'pydantic.fields',

    # Email Clients
    'imaplib',
    'smtplib',
    'email.mime',
    'google.auth',
    'google.oauth2',
    'googleapiclient.discovery',

    # LangChain
    'langchain',
    'langchain_community',
    'langchain_community.llms',
    'langchain_community.embeddings',
    'langchain_community.vectorstores',
    'langchain_chroma',
    'langchain_openai',
    'langchain_google_genai',
    'langchain_anthropic',

    # ChromaDB
    'chromadb',
    'chromadb.api',
    'chromadb.config',

    # Celery (optional, falls verwendet)
    'celery',
    'celery.app',
    'celery.worker',
    'celery.backends.redis',

    # Redis
    'redis',
    'redis.connection',

    # Utilities
    'loguru',
    'python-dotenv',
    'email_reply_parser',
]

# Automatisch alle Submodule von großen Packages sammeln
hidden_imports.extend(collect_submodules('langchain_community'))
hidden_imports.extend(collect_submodules('chromadb'))

# Data-Files (Templates, Config-Dateien, etc.)
datas = [
    # Source-Code (für Imports)
    (os.path.join(backend_dir, 'src'), 'src'),

    # .env-Template (optional)
    # (os.path.join(backend_dir, '.env.example'), '.'),
]

# Zusätzliche Data-Files von Packages
datas.extend(collect_data_files('chromadb'))
datas.extend(collect_data_files('langchain'))

a = Analysis(
    # Einstiegspunkt: main.py mit Uvicorn-Start
    [os.path.join(backend_dir, 'src', 'main_standalone.py')],

    pathex=[backend_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Unnötige Packages ausschließen (reduziert Binary-Größe)
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'pandas',
        'numpy.testing',
        'scipy',
        'PIL',
        'pygame',
        'PyQt5',
        'wx',
        'sphinx',
        'pytest',
        'hypothesis',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mail-assistant-backend',
    debug=False,  # Production: False (kein Debug-Output)
    bootloader_ignore_signals=False,
    strip=False,  # Linux: True (reduziert Größe), Windows: False
    upx=True,  # UPX-Kompression (optional, kann Probleme verursachen)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console-Window zeigen (für Logs), False für GUI-only
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'frontend', 'assets', 'icon.ico') if os.path.exists(os.path.join(project_root, 'frontend', 'assets', 'icon.ico')) else None
)
