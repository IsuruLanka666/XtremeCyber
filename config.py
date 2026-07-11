"""
XtremeCyber Configuration
Author: Isuru Lankadhikari
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------

APP_NAME = "XtremeCyber"

VERSION = "1.0.0"

AUTHOR = "Isuru Lankadhikari"

# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "assets"

DATABASE_DIR = BASE_DIR / "database"

EXPORT_DIR = BASE_DIR / "exports"

LOG_DIR = BASE_DIR / "logs"

SCREENSHOT_DIR = BASE_DIR / "screenshots"

# -------------------------------------------------

DATABASE_NAME = "xtremecyber.db"

DATABASE_PATH = DATABASE_DIR / DATABASE_NAME

# -------------------------------------------------

LOG_FILE = LOG_DIR / "xtremecyber.log"

# -------------------------------------------------

WINDOW_WIDTH = 1400

WINDOW_HEIGHT = 900

# -------------------------------------------------

THEME = "dark"

# -------------------------------------------------

MAX_THREADS = 100

SCAN_TIMEOUT = 3

DEFAULT_PORT_RANGE = "1-1000"

# -------------------------------------------------

EMAIL_ENABLED = os.getenv("XTREMECYBER_EMAIL_ENABLED","false",).lower() == "true"

SMTP_SERVER = os.getenv("XTREMECYBER_SMTP_SERVER","smtp.gmail.com",)

SMTP_PORT = int(os.getenv("XTREMECYBER_SMTP_PORT","587",))

EMAIL = os.getenv("XTREMECYBER_EMAIL","",)

PASSWORD = os.getenv("XTREMECYBER_PASSWORD","",)