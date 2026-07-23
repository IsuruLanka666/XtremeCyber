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

# Maximum host x port checks allowed in one scan.
MAX_SCAN_OPERATIONS = 200_000

# Maximum bytes read during safe banner collection.
BANNER_MAX_BYTES = 256

# Store closed TCP results in SQLite.
# False is recommended because a large scan can contain many closed ports.
PERSIST_CLOSED_SCAN_RESULTS = False

# Persist live counters after this many completed TCP checks.
SCAN_PROGRESS_DB_INTERVAL = 50

# Maximum saved findings displayed by the Results page per query.
RESULTS_QUERY_LIMIT = 5000

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

# -------------------------------------------------
# NVD CVE intelligence
# -------------------------------------------------

NVD_API_KEY = os.getenv("NVD_API_KEY", "")
NVD_API_TIMEOUT = 30
NVD_REQUEST_DELAY_SECONDS = 0.7 if NVD_API_KEY else 6.2
NVD_CPE_CACHE_DAYS = 30
NVD_CVE_CACHE_DAYS = 7