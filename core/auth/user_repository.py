"""
Database access for XtremeCyber users.
"""

from __future__ import annotations
from typing import Any

from core.database.database import DatabaseManager, database_manager
from core.exceptions import RepositoryError
from core.helpers import utc_now_iso


class UserRepository:
    """Create, retrieve, update, and list user records."""

    def __init__(self, database: DatabaseManager | None = None) -> None:
        self.database = database or database_manager

    def create_user(
        self,
        username: str,
        password_hash: str,
        email: str | None = None,
        role: str = "viewer",
    ) -> int:
        try:
            timestamp = utc_now_iso()
            return self.database.execute(
                """
                INSERT INTO users (
                    username, email, password_hash, role,
                    is_active, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    username.strip(),
                    email.strip() if email else None,
                    password_hash,
                    role,
                    timestamp,
                    timestamp,
                ),
            )
        except Exception as exc:
            raise RepositoryError(
                f"Could not create user '{username}'."
            ) from exc

    def get_by_username(self, username: str) -> dict[str, Any] | None:
        row = self.database.fetch_one(
            "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
            (username.strip(),),
        )
        return dict(row) if row else None

    def get_by_id(self, user_id: int) -> dict[str, Any] | None:
        row = self.database.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        )
        return dict(row) if row else None

    def username_exists(self, username: str) -> bool:
        return self.get_by_username(username) is not None

    def email_exists(
        self,
        email: str,
        excluding_user_id: int | None = None,
    ) -> bool:
        if excluding_user_id is None:
            row = self.database.fetch_one(
                "SELECT id FROM users WHERE email = ? COLLATE NOCASE",
                (email.strip(),),
            )
        else:
            row = self.database.fetch_one(
                """
                SELECT id FROM users
                WHERE email = ? COLLATE NOCASE AND id != ?
                """,
                (email.strip(), excluding_user_id),
            )
        return row is not None

    def count_users(self) -> int:
        row = self.database.fetch_one(
            "SELECT COUNT(*) AS total FROM users"
        )
        return int(row["total"]) if row else 0

    def count_active_admins(self) -> int:
        row = self.database.fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM users
            WHERE role = 'admin' AND is_active = 1
            """
        )
        return int(row["total"]) if row else 0

    def list_users(self) -> list[dict[str, Any]]:
        rows = self.database.fetch_all(
            """
            SELECT id, username, email, role, is_active,
                   created_at, updated_at, last_login_at
            FROM users
            ORDER BY username COLLATE NOCASE
            """
        )
        return [dict(row) for row in rows]

    def update_last_login(self, user_id: int) -> None:
        timestamp = utc_now_iso()
        self.database.execute(
            """
            UPDATE users
            SET last_login_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (timestamp, timestamp, user_id),
        )

    def update_password(self, user_id: int, password_hash: str) -> None:
        self.database.execute(
            """
            UPDATE users
            SET password_hash = ?, updated_at = ?
            WHERE id = ?
            """,
            (password_hash, utc_now_iso(), user_id),
        )

    def update_role(self, user_id: int, role: str) -> None:
        self.database.execute(
            """
            UPDATE users
            SET role = ?, updated_at = ?
            WHERE id = ?
            """,
            (role, utc_now_iso(), user_id),
        )

    def update_profile(self, user_id: int, email: str | None) -> None:
        self.database.execute(
            """
            UPDATE users
            SET email = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                email.strip() if email else None,
                utc_now_iso(),
                user_id,
            ),
        )

    def set_active(self, user_id: int, is_active: bool) -> None:
        self.database.execute(
            """
            UPDATE users
            SET is_active = ?, updated_at = ?
            WHERE id = ?
            """,
            (1 if is_active else 0, utc_now_iso(), user_id),
        )
