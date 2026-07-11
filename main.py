"""
XtremeCyber

Main Entry Point
"""

import sys

from pathlib import Path

from config import *

def create_directories():

    directories = [

        ASSETS_DIR,

        DATABASE_DIR,

        EXPORT_DIR,

        LOG_DIR,

        SCREENSHOT_DIR

    ]

    for folder in directories:

        Path(folder).mkdir(parents=True, exist_ok=True)

def startup():

    print("=" * 60)

    print(APP_NAME)

    print("Version :", VERSION)

    print("Starting...")

    print("=" * 60)

def main():

    create_directories()

    startup()

    print("Project initialized successfully.")

if __name__ == "__main__":

    main()