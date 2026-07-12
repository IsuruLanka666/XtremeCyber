"""
XtremeCyber application entry point.
"""

import sys
from pathlib import Path

from config import (
    APP_NAME,
    AUTHOR,
    DATABASE_PATH,
    VERSION,
)
from core.database.database import database_manager
from core.exceptions import XtremeCyberError
from core.helpers import ensure_directories
from core.logger import configure_logging


def print_startup_banner() -> None:
    """Display basic application startup information."""

    print("=" * 68)
    print(f"{APP_NAME} - Automated Vulnerability Assessment Platform")
    print(f"Version: {VERSION}")
    print(f"Author:  {AUTHOR}")
    print("=" * 68)


def initialize_application() -> None:
    """Initialize directories, logging, and the database."""

    ensure_directories()

    logger = configure_logging()

    logger.info("Starting %s version %s", APP_NAME, VERSION)

    database_manager.initialize()

    logger.info("Application initialization completed.")
    logger.info("Database location: %s", DATABASE_PATH)


def main() -> int:
    """Run the XtremeCyber application."""

    print_startup_banner()

    try:
        initialize_application()

        print("Application foundation initialized successfully.")
        print(f"Database created at: {Path(DATABASE_PATH)}")
        print("Log file created inside the logs folder.")

        return 0

    except XtremeCyberError as exc:
        print(f"XtremeCyber startup error: {exc}")
        return 1

    except Exception as exc:
        print(f"Unexpected startup error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
