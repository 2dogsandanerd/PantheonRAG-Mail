# Logging System Fix

## Problem

Aktuell:
- **Logging-Level:** `WARNING` (nur Warnungen + Fehler)
- **Keine INFO-Logs:** Normale Aktivität nicht sichtbar
- **Log-Files gelöscht:** `clear_logs()` löscht beim Start ALLE Logs
- **Nicht konfigurierbar:** Level ist hardcoded in `crash_detector.py`

**Ergebnis:** User sieht keine Logs, `/logs/` ist leer

---

## Lösung 1: Umgebungsvariable für Log-Level (Empfohlen)

### Implementation

**Datei:** `backend/src/utils/crash_detector.py`

**Änderung:**
```python
def _setup_logging(self):
    """Setup enhanced logging with configurable level."""
    import os

    # Remove default logger
    logger.remove()

    # Get log level from environment (default: WARNING for production)
    console_level = os.getenv("LOG_LEVEL_CONSOLE", "WARNING")
    file_level = os.getenv("LOG_LEVEL_FILE", "INFO")  # File gets more detail

    # Console: Configurable level with color coding
    logger.add(
        sys.stderr,
        level=console_level,  # ← Changed from hardcoded "WARNING"
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        colorize=True
    )

    # Main log file (configurable level)
    logger.add(
        self.log_dir / "backend.log",
        level=file_level,  # ← Changed from hardcoded "WARNING"
        rotation="50 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | PID:{process} | {message}",
        enqueue=True
    )

    # ... rest unchanged
```

**Usage:**
```bash
# Development: Full logging
export LOG_LEVEL_CONSOLE=DEBUG
export LOG_LEVEL_FILE=DEBUG
uvicorn src.main:app --reload

# Production: Only warnings/errors on console, INFO to file
export LOG_LEVEL_CONSOLE=WARNING
export LOG_LEVEL_FILE=INFO
uvicorn src.main:app

# Quick debug: Verbose console
LOG_LEVEL_CONSOLE=DEBUG uvicorn src.main:app --reload
```

**Add to `.env`:**
```bash
# Logging Configuration
LOG_LEVEL_CONSOLE=DEBUG    # Console log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL_FILE=INFO        # File log level (usually one level more verbose than console)
```

---

## Lösung 2: Conditional `clear_logs()` (Empfohlen)

### Problem

Beim Start werden ALLE Logs gelöscht - auch wichtige Crash-Reports!

```python
# crash_detector.py:97
def clear_logs(self):
    """Clears all .log and .json files from the log directory on startup."""
    logger.info(f"Clearing old logs from {self.log_dir}...")
    cleared_count = 0
    try:
        for log_file in self.log_dir.glob("*.log"):
            log_file.unlink()  # ← Löscht ALLES!
```

### Fix

```python
def clear_logs(self):
    """Conditionally clear old logs based on environment."""
    import os

    # Only clear logs if explicitly enabled
    if os.getenv("CLEAR_LOGS_ON_STARTUP", "false").lower() != "true":
        logger.info("Log clearing disabled (set CLEAR_LOGS_ON_STARTUP=true to enable)")
        return

    logger.info(f"Clearing old logs from {self.log_dir}...")
    cleared_count = 0
    try:
        # Only clear regular logs, KEEP crash reports
        for log_file in self.log_dir.glob("*.log"):
            # Skip crash logs (keep for debugging)
            if "crash" in log_file.name:
                continue

            log_file.unlink()
            cleared_count += 1

        # Clear crash JSON reports only if older than 7 days
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=7)

        for crash_report in self.log_dir.glob("crash_*.json"):
            if crash_report.stat().st_mtime < cutoff.timestamp():
                crash_report.unlink()
                cleared_count += 1

        if cleared_count > 0:
            logger.info(f"Successfully cleared {cleared_count} old log file(s).")
        else:
            logger.info("No old log files to clear.")
    except OSError as e:
        logger.error(f"Error clearing log files: {e}")
```

**Add to `.env`:**
```bash
# Log Cleanup
CLEAR_LOGS_ON_STARTUP=false  # Set to 'true' to clear logs on startup (default: false)
```

---

## Lösung 3: Separate Development/Production Configs

### Create Log Profiles

**Datei:** `backend/src/utils/log_profiles.py` (NEW)

```python
"""
Logging profiles for different environments.
"""

import os
from typing import Dict

LOG_PROFILES = {
    "development": {
        "console_level": "DEBUG",
        "file_level": "DEBUG",
        "clear_on_startup": False,
        "rotation": "10 MB",
        "retention": "3 days"
    },
    "production": {
        "console_level": "WARNING",
        "file_level": "INFO",
        "clear_on_startup": False,
        "rotation": "50 MB",
        "retention": "30 days"
    },
    "testing": {
        "console_level": "ERROR",
        "file_level": "WARNING",
        "clear_on_startup": True,  # Clean logs between test runs
        "rotation": "5 MB",
        "retention": "1 day"
    }
}

def get_log_config() -> Dict:
    """Get logging configuration based on environment."""
    profile = os.getenv("LOG_PROFILE", "development")
    return LOG_PROFILES.get(profile, LOG_PROFILES["development"])
```

**Usage in `crash_detector.py`:**
```python
from src.utils.log_profiles import get_log_config

class CrashDetector:
    def __init__(self, log_dir: str = None):
        # ... existing code ...
        self.log_config = get_log_config()
        self._setup_logging()

        if self.log_config["clear_on_startup"]:
            self.clear_logs()

    def _setup_logging(self):
        # Use config values instead of hardcoded
        console_level = self.log_config["console_level"]
        file_level = self.log_config["file_level"]
        rotation = self.log_config["rotation"]
        retention = self.log_config["retention"]

        # ... rest of setup ...
```

**Add to `.env`:**
```bash
# Logging Profile (development, production, testing)
LOG_PROFILE=development
```

---

## Quick Fix (Immediate)

**Wenn du JETZT sofort Logs sehen willst:**

```bash
# 1. Setze Log-Level manuell (quick & dirty)
cd /mnt/dev/eingang/mail_modul_alpha/backend

# 2. Edit crash_detector.py - Zeile 50 und 58
sed -i 's/level="WARNING"/level="INFO"/g' src/utils/crash_detector.py

# 3. Edit crash_detector.py - Zeile 99 (disable clear_logs)
sed -i 's/def clear_logs(self):/def clear_logs(self):\n        return  # DISABLED/' src/utils/crash_detector.py

# 4. Backend neu starten
pkill -f uvicorn
source ../venv/bin/activate
uvicorn src.main:app --reload --port 33800
```

**Logs checken:**
```bash
# Watch logs in real-time
tail -f /mnt/dev/eingang/mail_modul_alpha/logs/backend.log

# Check if logs exist
ls -lh /mnt/dev/eingang/mail_modul_alpha/logs/
```

---

## Empfohlene Reihenfolge

1. ✅ **Quick Fix:** Setze `level="INFO"` in crash_detector.py (5 min)
2. ✅ **Conditional Clear:** Disable `clear_logs()` default (5 min)
3. ⏳ **Env Variables:** Add `LOG_LEVEL_*` support (10 min)
4. ⏳ **Log Profiles:** Create profile system (20 min)

---

**Total Effort:**
- Quick Fix: 5 min
- Full Solution: 40 min

**Priority:** ⭐⭐⭐ HIGH (wichtig für Debugging)
