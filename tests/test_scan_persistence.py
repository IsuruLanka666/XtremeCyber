"""
Tests for SQLite persistence lifecycle.
"""

from __future__ import annotations

import sqlite3
import unittest
from datetime import datetime, timezone

from core.scanning.models import ScanConfiguration, ScanProfile
from core.scanning.persistence import ScanRunRepository
from core.scanning.ports import parse_port_spec
from core.scanning.results import (
    PortScanResult,
    PortState,
    ScanProgress,
    ScanSummary,
)
from core.scanning.targets import parse_target


class SQLiteAdapter:
    """Small adapter matching the XtremeCyber DatabaseManager methods."""

    def __init__(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row

    def execute(self, query: str, parameters: tuple = ()) -> int:
        cursor = self.connection.execute(query, parameters)
        self.connection.commit()
        return int(cursor.lastrowid or 0)

    def fetch_one(self, query: str, parameters: tuple = ()):
        return self.connection.execute(
            query,
            parameters,
        ).fetchone()

    def fetch_all(self, query: str, parameters: tuple = ()):
        return self.connection.execute(
            query,
            parameters,
        ).fetchall()


def configuration() -> ScanConfiguration:
    return ScanConfiguration(
        target=parse_target("127.0.0.1"),
        ports=parse_port_spec("80,443"),
        profile=ScanProfile.CUSTOM,
        max_workers=10,
        timeout_seconds=1.0,
        banner_grab=True,
        resolve_hostname=True,
        authorization_confirmed=True,
    )


class ScanPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.database = SQLiteAdapter()
        self.repository = ScanRunRepository(self.database)

    def test_complete_scan_lifecycle(self) -> None:
        scan_id = self.repository.create_scan(
            configuration(),
            user_id=1,
        )

        self.repository.add_result(
            scan_id,
            PortScanResult(
                host="127.0.0.1",
                resolved_address="127.0.0.1",
                port=80,
                state=PortState.OPEN,
                service="http",
                banner="HTTP/1.0 200 OK",
                latency_ms=1.25,
            ),
        )

        self.repository.update_progress(
            scan_id,
            ScanProgress(
                completed=2,
                total=2,
                open_ports=1,
                closed_ports=1,
                errors=0,
            ),
        )

        self.repository.finalize_scan(
            scan_id,
            ScanSummary(
                total=2,
                completed=2,
                open_ports=1,
                closed_ports=1,
                errors=0,
                cancelled=False,
                duration_seconds=0.5,
            ),
        )

        scan = self.repository.get_scan(scan_id)
        self.assertIsNotNone(scan)
        self.assertEqual(scan["status"], "completed")
        self.assertEqual(scan["open_ports"], 1)

        results = self.repository.get_results(scan_id)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["port"], 80)

    def test_running_scan_recovery(self) -> None:
        scan_id = self.repository.create_scan(
            configuration(),
            user_id=None,
        )

        recovered = self.repository.recover_interrupted_scans()
        scan = self.repository.get_scan(scan_id)

        self.assertEqual(recovered, 1)
        self.assertEqual(scan["status"], "interrupted")

    def test_dashboard_stats(self) -> None:
        self.repository.create_scan(
            configuration(),
            user_id=None,
        )

        stats = self.repository.dashboard_stats()

        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["running"], 1)


if __name__ == "__main__":
    unittest.main()
