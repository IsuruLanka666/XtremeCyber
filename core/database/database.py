"""
SQLite connection and database initialization management.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Generator

from config import (
    DATABASE_ENABLE_WAL,
    DATABASE_PATH,
    DATABASE_TIMEOUT,
)
from core.database.models import (
    CREATE_TABLES_SQL,
    default_setting_values,
    schema_metadata_values,
)
from core.exceptions import (
    DatabaseError,
    DatabaseInitializationError,
)
from core.helpers import utc_now_iso
from core.logger import get_logger


logger = get_logger(__name__)


class DatabaseManager:
    """
    Manage SQLite connections and schema initialization.

    A separate connection is opened for each operation. This is safer
    for the multithreaded scanning components that will be added later.
    """

    def __init__(self, database_path: Path | str = DATABASE_PATH) -> None:
        self.database_path = Path(database_path)
        self._initialization_lock = RLock()

    def initialize(self) -> None:
       
        with self._initialization_lock:
            try:
                self.database_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                with self.connection() as connection:
                    connection.executescript(CREATE_TABLES_SQL)

                    self._insert_schema_metadata(connection)
                    self._insert_default_settings(connection)

                logger.info(
                    "Database initialized successfully at %s",
                    self.database_path,
                )

            except sqlite3.Error as exc:
                logger.exception("Database initialization failed.")
                raise DatabaseInitializationError(
                    "XtremeCyber could not initialize its database."
                ) from exc

    def connect(self) -> sqlite3.Connection:
        """
        Create and configure a SQLite connection.

        Returns:
            Configured sqlite3.Connection.
        """

        try:
            connection = sqlite3.connect(
                self.database_path,
                timeout=DATABASE_TIMEOUT,
                detect_types=sqlite3.PARSE_DECLTYPES,
                check_same_thread=False,
            )

            connection.row_factory = sqlite3.Row

            connection.execute("PRAGMA foreign_keys = ON;")
            connection.execute("PRAGMA busy_timeout = 15000;")

            if DATABASE_ENABLE_WAL:
                connection.execute("PRAGMA journal_mode = WAL;")

            return connection

        except sqlite3.Error as exc:
            logger.exception(
                "Could not connect to database at %s",
                self.database_path,
            )
            raise DatabaseError(
                "Could not connect to the XtremeCyber database."
            ) from exc

    @contextmanager
    def connection(
        self,
    ) -> Generator[sqlite3.Connection, None, None]:
        """
        Provide a transaction-aware database connection.

        Commits when successful and rolls back when an exception occurs.
        """

        connection = self.connect()

        try:
            yield connection
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def execute(
        self,
        sql: str,
        parameters: tuple | dict = (),
    ) -> int:
        """
        Execute INSERT, UPDATE, or DELETE SQL.

        Returns:
            The inserted row ID, when available.
        """

        try:
            with self.connection() as connection:
                cursor = connection.execute(sql, parameters)
                return int(cursor.lastrowid or 0)

        except sqlite3.Error as exc:
            logger.exception("Database execute operation failed.")
            raise DatabaseError(
                "A database write operation failed."
            ) from exc

    def fetch_one(
        self,
        sql: str,
        parameters: tuple | dict = (),
    ) -> sqlite3.Row | None:
        """Execute a query and return one row."""

        try:
            with self.connection() as connection:
                cursor = connection.execute(sql, parameters)
                return cursor.fetchone()

        except sqlite3.Error as exc:
            logger.exception("Database fetch-one operation failed.")
            raise DatabaseError(
                "A database read operation failed."
            ) from exc

    def fetch_all(
        self,
        sql: str,
        parameters: tuple | dict = (),
    ) -> list[sqlite3.Row]:
        """Execute a query and return all rows."""

        try:
            with self.connection() as connection:
                cursor = connection.execute(sql, parameters)
                return list(cursor.fetchall())

        except sqlite3.Error as exc:
            logger.exception("Database fetch-all operation failed.")
            raise DatabaseError(
                "A database read operation failed."
            ) from exc

    @staticmethod
    def _insert_schema_metadata(
        connection: sqlite3.Connection,
    ) -> None:
        """Insert required schema metadata."""

        for key, value in schema_metadata_values().items():
            connection.execute(
                """
                INSERT INTO schema_metadata (key, value)
                VALUES (?, ?)
                ON CONFLICT(key)
                DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    @staticmethod
    def _insert_default_settings(
        connection: sqlite3.Connection,
    ) -> None:
        """Insert missing default settings."""

        timestamp = utc_now_iso()

        for key, value in default_setting_values().items():
            connection.execute(
                """
                INSERT OR IGNORE INTO settings (
                    key,
                    value,
                    updated_at
                )
                VALUES (?, ?, ?)
                """,
                (key, value, timestamp),
            )


database_manager = DatabaseManager()