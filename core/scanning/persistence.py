"""
SQLite persistence for XtremeCyber network scans and TCP findings.

"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

from core.database.database import DatabaseManager, database_manager
from core.exceptions import RepositoryError
from core.helpers import utc_now_iso
from core.logger import get_logger
from core.scanning.models import ScanConfiguration
from core.scanning.results import (
    PortScanResult,
    PortState,
    ScanProgress,
    ScanSummary,
)


logger = get_logger(__name__)

FINAL_SCAN_STATUSES = {
    "completed",
    "cancelled",
    "failed",
    "interrupted",
}


class ScanRunRepository:
    """Store scan lifecycle information and TCP findings."""

    def __init__(
        self,
        database: DatabaseManager | None = None,
    ) -> None:
        self.database = database or database_manager
        self.initialize_schema()

    def initialize_schema(self) -> None:
        """Create the Part 3 persistence tables and indexes."""

        statements = [
            """
            CREATE TABLE IF NOT EXISTS network_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                target TEXT NOT NULL,
                target_kind TEXT NOT NULL,
                profile TEXT NOT NULL,
                port_spec TEXT NOT NULL,
                host_count INTEGER NOT NULL,
                port_count INTEGER NOT NULL,
                total_operations INTEGER NOT NULL,
                max_workers INTEGER NOT NULL,
                timeout_seconds REAL NOT NULL,
                banner_grab INTEGER NOT NULL DEFAULT 0,
                resolve_hostname INTEGER NOT NULL DEFAULT 0,
                authorization_confirmed INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'running',
                completed_operations INTEGER NOT NULL DEFAULT 0,
                open_ports INTEGER NOT NULL DEFAULT 0,
                closed_ports INTEGER NOT NULL DEFAULT 0,
                errors INTEGER NOT NULL DEFAULT 0,
                duration_seconds REAL NOT NULL DEFAULT 0,
                error_message TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS network_scan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                host TEXT NOT NULL,
                resolved_address TEXT,
                port INTEGER NOT NULL,
                state TEXT NOT NULL,
                service TEXT,
                banner TEXT,
                latency_ms REAL,
                error TEXT,
                scanned_at TEXT NOT NULL,
                FOREIGN KEY (scan_id)
                    REFERENCES network_scans(id)
                    ON DELETE CASCADE,
                UNIQUE (
                    scan_id,
                    host,
                    resolved_address,
                    port
                )
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_network_scans_status
            ON network_scans(status)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_network_scans_created
            ON network_scans(created_at DESC)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_network_scan_results_scan
            ON network_scan_results(scan_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_network_scan_results_state
            ON network_scan_results(scan_id, state)
            """,
        ]

        try:
            for statement in statements:
                self.database.execute(statement)
        except Exception as exc:
            raise RepositoryError(
                "Could not initialize the network scan persistence schema."
            ) from exc

    def recover_interrupted_scans(self) -> int:
        """
        Mark scans left in the running state as interrupted.

        Call this once during application startup, before a new scan starts.
        """

        timestamp = utc_now_iso()

        try:
            row = self.database.fetch_one(
                """
                SELECT COUNT(*) AS total
                FROM network_scans
                WHERE status = 'running'
                """
            )
            total = int(row["total"]) if row else 0

            if total:
                self.database.execute(
                    """
                    UPDATE network_scans
                    SET
                        status = 'interrupted',
                        completed_at = ?,
                        updated_at = ?,
                        error_message = COALESCE(
                            error_message,
                            'Application closed before the scan completed.'
                        )
                    WHERE status = 'running'
                    """,
                    (timestamp, timestamp),
                )

                logger.warning(
                    "Recovered %s interrupted scan(s).",
                    total,
                )

            return total
        except Exception as exc:
            raise RepositoryError(
                "Could not recover interrupted scans."
            ) from exc

    def create_scan(
        self,
        configuration: ScanConfiguration,
        *,
        user_id: int | None,
    ) -> int:
        """Create a running scan record and return its ID."""

        timestamp = utc_now_iso()
        total_operations = (
            configuration.target.host_count
            * configuration.ports.count
        )

        try:
            scan_id = self.database.execute(
                """
                INSERT INTO network_scans (
                    user_id,
                    target,
                    target_kind,
                    profile,
                    port_spec,
                    host_count,
                    port_count,
                    total_operations,
                    max_workers,
                    timeout_seconds,
                    banner_grab,
                    resolve_hostname,
                    authorization_confirmed,
                    status,
                    created_at,
                    started_at,
                    updated_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    'running', ?, ?, ?
                )
                """,
                (
                    user_id,
                    configuration.target.normalized_value,
                    configuration.target.kind.value,
                    configuration.profile.value,
                    configuration.ports.normalized,
                    configuration.target.host_count,
                    configuration.ports.count,
                    total_operations,
                    configuration.max_workers,
                    configuration.timeout_seconds,
                    int(configuration.banner_grab),
                    int(configuration.resolve_hostname),
                    int(configuration.authorization_confirmed),
                    timestamp,
                    timestamp,
                    timestamp,
                ),
            )
        except Exception as exc:
            raise RepositoryError(
                "Could not create the scan history record."
            ) from exc

        logger.info(
            "Created persisted scan id=%s target=%s checks=%s.",
            scan_id,
            configuration.target.normalized_value,
            total_operations,
        )

        return int(scan_id)

    def add_result(
        self,
        scan_id: int,
        result: PortScanResult,
    ) -> None:
        """Insert or update a persisted TCP result."""

        try:
            self.database.execute(
                """
                INSERT INTO network_scan_results (
                    scan_id,
                    host,
                    resolved_address,
                    port,
                    state,
                    service,
                    banner,
                    latency_ms,
                    error,
                    scanned_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (
                    scan_id,
                    host,
                    resolved_address,
                    port
                )
                DO UPDATE SET
                    state = excluded.state,
                    service = excluded.service,
                    banner = excluded.banner,
                    latency_ms = excluded.latency_ms,
                    error = excluded.error,
                    scanned_at = excluded.scanned_at
                """,
                (
                    scan_id,
                    result.host,
                    result.resolved_address,
                    result.port,
                    result.state.value,
                    result.service,
                    result.banner,
                    result.latency_ms,
                    result.error,
                    result.scanned_at.isoformat(),
                ),
            )
        except Exception as exc:
            raise RepositoryError(
                f"Could not store a TCP result for scan {scan_id}."
            ) from exc

    def update_progress(
        self,
        scan_id: int,
        progress: ScanProgress,
    ) -> None:
        """Update the persisted live counters for a running scan."""

        try:
            self.database.execute(
                """
                UPDATE network_scans
                SET
                    completed_operations = ?,
                    open_ports = ?,
                    closed_ports = ?,
                    errors = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    progress.completed,
                    progress.open_ports,
                    progress.closed_ports,
                    progress.errors,
                    utc_now_iso(),
                    scan_id,
                ),
            )
        except Exception as exc:
            raise RepositoryError(
                f"Could not update progress for scan {scan_id}."
            ) from exc

    def finalize_scan(
        self,
        scan_id: int,
        summary: ScanSummary,
    ) -> None:
        """Finalize a completed or cancelled scan."""

        timestamp = utc_now_iso()
        status = "cancelled" if summary.cancelled else "completed"

        try:
            self.database.execute(
                """
                UPDATE network_scans
                SET
                    status = ?,
                    completed_operations = ?,
                    open_ports = ?,
                    closed_ports = ?,
                    errors = ?,
                    duration_seconds = ?,
                    completed_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    status,
                    summary.completed,
                    summary.open_ports,
                    summary.closed_ports,
                    summary.errors,
                    summary.duration_seconds,
                    timestamp,
                    timestamp,
                    scan_id,
                ),
            )
        except Exception as exc:
            raise RepositoryError(
                f"Could not finalize scan {scan_id}."
            ) from exc

    def fail_scan(
        self,
        scan_id: int,
        message: str,
    ) -> None:
        """Mark a scan as failed."""

        timestamp = utc_now_iso()

        try:
            self.database.execute(
                """
                UPDATE network_scans
                SET
                    status = 'failed',
                    error_message = ?,
                    completed_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    message[:2000],
                    timestamp,
                    timestamp,
                    scan_id,
                ),
            )
        except Exception as exc:
            raise RepositoryError(
                f"Could not mark scan {scan_id} as failed."
            ) from exc

    def get_scan(
        self,
        scan_id: int,
    ) -> dict[str, Any] | None:
        row = self.database.fetch_one(
            """
            SELECT *
            FROM network_scans
            WHERE id = ?
            """,
            (scan_id,),
        )

        return dict(row) if row else None

    def get_recent_scans(
        self,
        *,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        rows = self.database.fetch_all(
            """
            SELECT
                id,
                user_id,
                target,
                target_kind,
                profile,
                port_spec,
                host_count,
                port_count,
                total_operations,
                status,
                completed_operations,
                open_ports,
                closed_ports,
                errors,
                duration_seconds,
                error_message,
                created_at,
                started_at,
                completed_at,
                updated_at
            FROM network_scans
            ORDER BY id DESC
            LIMIT ?
            """,
            (max(1, int(limit)),),
        )

        return [dict(row) for row in rows]

    def get_recent(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Compatibility result for the existing dashboard table.

        The aliases match the earlier MainWindow `_populate_recent_scans`.
        """

        scans = self.get_recent_scans(limit=limit)

        return [
            {
                **scan,
                "scan_type": scan["profile"],
            }
            for scan in scans
        ]

    def count_all(self) -> int:
        row = self.database.fetch_one(
            "SELECT COUNT(*) AS total FROM network_scans"
        )

        return int(row["total"]) if row else 0

    def dashboard_stats(self) -> dict[str, int]:
        row = self.database.fetch_one(
            """
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE WHEN status = 'running' THEN 1 ELSE 0 END
                ) AS running,
                SUM(
                    CASE WHEN status = 'completed' THEN 1 ELSE 0 END
                ) AS completed,
                SUM(
                    CASE
                        WHEN status IN (
                            'failed',
                            'cancelled',
                            'interrupted'
                        )
                        THEN 1
                        ELSE 0
                    END
                ) AS incomplete,
                COALESCE(SUM(open_ports), 0) AS open_ports
            FROM network_scans
            """
        )

        if row is None:
            return {
                "total": 0,
                "running": 0,
                "completed": 0,
                "incomplete": 0,
                "open_ports": 0,
            }

        return {
            "total": int(row["total"] or 0),
            "running": int(row["running"] or 0),
            "completed": int(row["completed"] or 0),
            "incomplete": int(row["incomplete"] or 0),
            "open_ports": int(row["open_ports"] or 0),
        }

    def get_results(
        self,
        scan_id: int,
        *,
        states: Iterable[str] | None = None,
        search: str = "",
        limit: int = 5000,
    ) -> list[dict[str, Any]]:
        clauses = ["scan_id = ?"]
        parameters: list[Any] = [scan_id]

        normalized_states = tuple(
            state.strip().lower()
            for state in (states or ())
            if state.strip()
        )

        if normalized_states:
            placeholders = ",".join("?" for _ in normalized_states)
            clauses.append(f"state IN ({placeholders})")
            parameters.extend(normalized_states)

        normalized_search = search.strip()

        if normalized_search:
            clauses.append(
                """
                (
                    host LIKE ?
                    OR resolved_address LIKE ?
                    OR service LIKE ?
                    OR banner LIKE ?
                    OR error LIKE ?
                    OR CAST(port AS TEXT) LIKE ?
                )
                """
            )
            pattern = f"%{normalized_search}%"
            parameters.extend([pattern] * 6)

        parameters.append(max(1, int(limit)))

        query = f"""
            SELECT
                id,
                scan_id,
                host,
                resolved_address,
                port,
                state,
                service,
                banner,
                latency_ms,
                error,
                scanned_at
            FROM network_scan_results
            WHERE {' AND '.join(clauses)}
            ORDER BY
                CASE state
                    WHEN 'open' THEN 0
                    WHEN 'error' THEN 1
                    WHEN 'closed' THEN 2
                    ELSE 3
                END,
                host,
                port
            LIMIT ?
        """

        rows = self.database.fetch_all(
            query,
            tuple(parameters),
        )

        return [dict(row) for row in rows]

    def result_counts(
        self,
        scan_id: int,
    ) -> dict[str, int]:
        row = self.database.fetch_one(
            """
            SELECT
                COUNT(*) AS stored,
                SUM(
                    CASE WHEN state = 'open' THEN 1 ELSE 0 END
                ) AS open,
                SUM(
                    CASE WHEN state = 'closed' THEN 1 ELSE 0 END
                ) AS closed,
                SUM(
                    CASE WHEN state = 'error' THEN 1 ELSE 0 END
                ) AS errors
            FROM network_scan_results
            WHERE scan_id = ?
            """,
            (scan_id,),
        )

        if row is None:
            return {
                "stored": 0,
                "open": 0,
                "closed": 0,
                "errors": 0,
            }

        return {
            "stored": int(row["stored"] or 0),
            "open": int(row["open"] or 0),
            "closed": int(row["closed"] or 0),
            "errors": int(row["errors"] or 0),
        }


@dataclass(slots=True)
class ScanRunRecorder:
    """
    Throttle scan progress writes and persist selected result states.

    Open ports and errors are persisted by default. Closed ports can be
    enabled through `persist_closed_results`.
    """

    repository: ScanRunRepository
    scan_id: int
    persist_closed_results: bool = False
    progress_interval: int = 50
    _last_progress_write: int = 0

    def record_result(
        self,
        result: PortScanResult,
    ) -> None:
        if (
            result.state == PortState.CLOSED
            and not self.persist_closed_results
        ):
            return

        self.repository.add_result(
            self.scan_id,
            result,
        )

    def record_progress(
        self,
        progress: ScanProgress,
    ) -> None:
        should_write = (
            progress.completed == progress.total
            or progress.completed - self._last_progress_write
            >= max(1, self.progress_interval)
        )

        if not should_write:
            return

        self.repository.update_progress(
            self.scan_id,
            progress,
        )
        self._last_progress_write = progress.completed

    def complete(
        self,
        summary: ScanSummary,
    ) -> None:
        self.repository.finalize_scan(
            self.scan_id,
            summary,
        )

    def fail(
        self,
        message: str,
    ) -> None:
        self.repository.fail_scan(
            self.scan_id,
            message,
        )
