"""
XtremeCyber Configuration
Author: Isuru Lankadhikari
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv()

# -------------------------------------------------
# App Info
# -------------------------------------------------

APP_NAME = "XtremeCyber"

VERSION = "1.0.0"

AUTHOR = "Isuru Lankadhikari"

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

THEME = os.getenv("XTREMECYBER_THEME", "dark").strip().lower()

# -------------------------------------------------
# Directories
# -------------------------------------------------

ASSETS_DIR = BASE_DIR / "assets"

DATABASE_DIR = BASE_DIR / "database"

EXPORT_DIR = BASE_DIR / "exports"

LOG_DIR = BASE_DIR / "logs"

SCREENSHOT_DIR = BASE_DIR / "screenshots"

# -------------------------------------------------
# Database Configuration
# -------------------------------------------------

DATABASE_NAME = "xtremecyber.db"

DATABASE_PATH = DATABASE_DIR / DATABASE_NAME

DATABASE_TIMEOUT = 15

DATABASE_ENABLE_WAL = True

# -------------------------------------------------
# Logging Configuration
# -------------------------------------------------

LOG_FILE = LOG_DIR / "xtremecyber.log"
LOG_LEVEL = os.getenv("XTREMECYBER_LOG_LEVEL", "INFO").strip().upper()
LOG_MAX_BYTES = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 5

# -------------------------------------------------
# Scanning 
# -------------------------------------------------

MAX_THREADS = 100
SCAN_TIMEOUT = 3.0
DEFAULT_PORT_RANGE = "1-1000"

MIN_PORT = 1
MAX_PORT = 65535

MAX_TARGETS_PER_SCAN = 256

SESSION_TIMEOUT_MINUTES = 30

# -------------------------------------------------
# Email Configuration
# -------------------------------------------------

EMAIL_ENABLED = os.getenv("XTREMECYBER_EMAIL_ENABLED","false",).strip().lower() == "true"

SMTP_SERVER = os.getenv("XTREMECYBER_SMTP_SERVER","smtp.gmail.com",)

SMTP_PORT = int(os.getenv("XTREMECYBER_SMTP_PORT","587",))

EMAIL = os.getenv("XTREMECYBER_EMAIL","",)

PASSWORD = os.getenv("XTREMECYBER_PASSWORD","",)