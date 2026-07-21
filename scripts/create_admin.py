"""
Create the first XtremeCyber administrator account.

"""

from __future__ import annotations

import getpass
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from core.auth.service import AuthenticationService
from core.database.database import database_manager
from core.exceptions import XtremeCyberError
from core.helpers import ensure_directories


def main() -> int:
    ensure_directories()
    database_manager.initialize()

    service = AuthenticationService()

    print("=" * 60)
    print("XtremeCyber Initial Administrator Setup")
    print("=" * 60)

    username = input("Administrator username: ").strip()
    email = input("Email address (optional): ").strip() or None
    password = getpass.getpass("Password: ")
    confirmation = getpass.getpass("Confirm password: ")

    if password != confirmation:
        print("Passwords do not match.")
        return 1

    try:
        user_id = service.create_initial_admin(
            username=username,
            password=password,
            email=email,
        )
    except XtremeCyberError as exc:
        print(f"Could not create administrator: {exc}")
        return 1

    print(f"Administrator account created successfully. User ID: {user_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
