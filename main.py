"""
XtremeCyber application entry point.
"""

import sys

from ui.app import run_application


def main() -> int:
    """Launch the XtremeCyber desktop application."""

    return run_application()


if __name__ == "__main__":
    sys.exit(main())