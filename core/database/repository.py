"""
Repository classes used to access XtremeCyber database records.
"""

from __future__ import annotations

import json
from typing import Any

from core.constants import ScanStatus, ScanType
from core.database.database import DatabaseManager, database_manager
from core.exceptions import RepositoryError
from core.helpers import utc_now_iso
from core.logger import get_logger


logger = get_logger(__name__)


class BaseRepository:
    """Base class shared by all repositories."""

    def __init__(
        self,
        database: DatabaseManager | None = None,
    ) -> None:
        self.database = database or database_manager


class SettingsRepository(BaseRepository):
    """Read and update application settings."""

    def get(self, key: str, default: str | None = None) -> str | None:
        row = self.database.fetch_one(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
        )

        if row is None:
            return default

        return str(row["value"])

    def get_all(self) -> dict[str, str]:
        rows = self.database.fetch_all(
            "SELECT key, value FROM settings ORDER BY key"
        )

        return {
            str(row["key"]): str(row["value"])
            for row in rows
        }

    def set(self, key: str, value: str) -> None:
        try:
            self.database.execute(
                """
                INSERT INTO settings (
                    key,
                    value,
                    updated_at
                )
                VALUES (?, ?, ?)
                ON CONFLICT(key)
                DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (key, value, utc_now_iso()),
            )

        except Exception as exc:
            raise RepositoryError(
                f"Could not save setting '{key}'."
            ) from exc


class ScanRepository(BaseRepository):
    """Create and manage vulnerability scan records."""

    def create_scan(
        self,
        target: str,
        scan_type: ScanType | str,
        port_range: str | None = None,
        created_by: int | None = None,
    ) -> int:
        scan_type_value = (
            scan_type.value
            if isinstance(scan_type, ScanType)
            else str(scan_type)
        )

        try:
            return self.database.execute(
                """
                INSERT INTO scan_history (
                    target,
                    scan_type,
                    port_range,
                    status,
                    created_by,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    target,
                    scan_type_value,
                    port_range,
                    ScanStatus.PENDING.value,
                    created_by,
                    utc_now_iso(),
                ),
            )

        except Exception as exc:
            raise RepositoryError(
                "Could not create the scan record."
            ) from exc

    def mark_running(self, scan_id: int) -> None:
        self._update_status(
            scan_id=scan_id,
            status=ScanStatus.RUNNING,
            started_at=utc_now_iso(),
        )

    def mark_completed(
        self,
        scan_id: int,
        duration_seconds: float,
        hosts_discovered: int = 0,
        open_ports: int = 0,
        vulnerabilities_found: int = 0,
        critical_count: int = 0,
        high_count: int = 0,
        medium_count: int = 0,
        low_count: int = 0,
    ) -> None:
        try:
            self.database.execute(
                """
                UPDATE scan_history
                SET
                    status = ?,
                    completed_at = ?,
                    duration_seconds = ?,
                    hosts_discovered = ?,
                    open_ports = ?,
                    vulnerabilities_found = ?,
                    critical_count = ?,
                    high_count = ?,
                    medium_count = ?,
                    low_count = ?
                WHERE id = ?
                """,
                (
                    ScanStatus.COMPLETED.value,
                    utc_now_iso(),
                    duration_seconds,
                    hosts_discovered,
                    open_ports,
                    vulnerabilities_found,
                    critical_count,
                    high_count,
                    medium_count,
                    low_count,
                    scan_id,
                ),
            )

        except Exception as exc:
            raise RepositoryError(
                f"Could not complete scan {scan_id}."
            ) from exc

    def mark_failed(
        self,
        scan_id: int,
        error_message: str,
    ) -> None:
        try:
            self.database.execute(
                """
                UPDATE scan_history
                SET
                    status = ?,
                    completed_at = ?,
                    error_message = ?
                WHERE id = ?
                """,
                (
                    ScanStatus.FAILED.value,
                    utc_now_iso(),
                    error_message,
                    scan_id,
                ),
            )

        except Exception as exc:
            raise RepositoryError(
                f"Could not mark scan {scan_id} as failed."
            ) from exc

    def get_by_id(self, scan_id: int) -> dict[str, Any] | None:
        row = self.database.fetch_one(
            "SELECT * FROM scan_history WHERE id = ?",
            (scan_id,),
        )

        return dict(row) if row else None

    def get_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit), 100))

        rows = self.database.fetch_all(
            """
            SELECT *
            FROM scan_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (safe_limit,),
        )

        return [dict(row) for row in rows]

    def count_all(self) -> int:
        row = self.database.fetch_one(
            "SELECT COUNT(*) AS total FROM scan_history"
        )

        return int(row["total"]) if row else 0

    def _update_status(
        self,
        scan_id: int,
        status: ScanStatus,
        started_at: str | None = None,
    ) -> None:
        try:
            self.database.execute(
                """
                UPDATE scan_history
                SET
                    status = ?,
                    started_at = COALESCE(?, started_at)
                WHERE id = ?
                """,
                (
                    status.value,
                    started_at,
                    scan_id,
                ),
            )

        except Exception as exc:
            raise RepositoryError(
                f"Could not update scan {scan_id}."
            ) from exc


class HostRepository(BaseRepository):
    """Store hosts discovered during scans."""

    def create_host(
        self,
        scan_id: int,
        ip_address: str,
        hostname: str | None = None,
        status: str = "unknown",
        response_time_ms: float | None = None,
    ) -> int:
        try:
            return self.database.execute(
                """
                INSERT INTO hosts (
                    scan_id,
                    ip_address,
                    hostname,
                    status,
                    response_time_ms,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_id,
                    ip_address,
                    hostname,
                    status,
                    response_time_ms,
                    utc_now_iso(),
                ),
            )

        except Exception as exc:
            raise RepositoryError(
                f"Could not save host {ip_address}."
            ) from exc

    def get_for_scan(self, scan_id: int) -> list[dict[str, Any]]:
        rows = self.database.fetch_all(
            """
            SELECT *
            FROM hosts
            WHERE scan_id = ?
            ORDER BY ip_address
            """,
            (scan_id,),
        )

        return [dict(row) for row in rows]


class PortRepository(BaseRepository):
    """Store port and service information."""

    def create_port(
        self,
        host_id: int,
        port_number: int,
        protocol: str = "tcp",
        state: str = "open",
        service_name: str | None = None,
        product: str | None = None,
        version: str | None = None,
        banner: str | None = None,
    ) -> int:
        try:
            return self.database.execute(
                """
                INSERT INTO ports (
                    host_id,
                    port_number,
                    protocol,
                    state,
                    service_name,
                    product,
                    version,
                    banner,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    host_id,
                    port_number,
                    protocol,
                    state,
                    service_name,
                    product,
                    version,
                    banner,
                    utc_now_iso(),
                ),
            )

        except Exception as exc:
            raise RepositoryError(
                f"Could not save port {port_number}/{protocol}."
            ) from exc


class VulnerabilityRepository(BaseRepository):
    """Store detected vulnerabilities."""

    def create_vulnerability(
        self,
        scan_id: int,
        title: str,
        severity: str,
        host_id: int | None = None,
        port_id: int | None = None,
        cve_id: str | None = None,
        description: str | None = None,
        cvss_score: float | None = None,
        affected_component: str | None = None,
        recommendation: str | None = None,
        reference_url: str | None = None,
    ) -> int:
        try:
            return self.database.execute(
                """
                INSERT INTO vulnerabilities (
                    scan_id,
                    host_id,
                    port_id,
                    cve_id,
                    title,
                    description,
                    severity,
                    cvss_score,
                    affected_component,
                    recommendation,
                    reference_url,
                    detected_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_id,
                    host_id,
                    port_id,
                    cve_id,
                    title,
                    description,
                    severity,
                    cvss_score,
                    affected_component,
                    recommendation,
                    reference_url,
                    utc_now_iso(),
                ),
            )

        except Exception as exc:
            raise RepositoryError(
                f"Could not save vulnerability '{title}'."
            ) from exc


class ApplicationLogRepository(BaseRepository):
    """Store important audit and application events."""

    def create_log(
        self,
        level: str,
        event_type: str,
        message: str,
        details: dict[str, Any] | None = None,
        user_id: int | None = None,
    ) -> int:
        serialized_details = (
            json.dumps(details, ensure_ascii=False)
            if details is not None
            else None
        )

        return self.database.execute(
            """
            INSERT INTO app_logs (
                user_id,
                level,
                event_type,
                message,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                level.upper(),
                event_type,
                message,
                serialized_details,
                utc_now_iso(),
            ),
        )