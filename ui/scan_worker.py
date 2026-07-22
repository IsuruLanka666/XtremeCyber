"""
Qt worker bridge for the synchronous TCP scan engine.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from core.scanning.engine import ScanEngine
from core.scanning.models import ScanConfiguration


class ScanWorker(QObject):
    """Run ScanEngine inside a QThread and forward thread-safe signals."""

    result_ready = Signal(object)
    progress_changed = Signal(object)
    status_changed = Signal(str)
    scan_finished = Signal(object)
    scan_failed = Signal(str)

    def __init__(
        self,
        configuration: ScanConfiguration,
        *,
        max_operations: int,
        banner_max_bytes: int,
    ) -> None:
        super().__init__()

        self.engine = ScanEngine(
            configuration,
            result_callback=self.result_ready.emit,
            progress_callback=self.progress_changed.emit,
            status_callback=self.status_changed.emit,
            max_operations=max_operations,
            banner_max_bytes=banner_max_bytes,
        )

    @Slot()
    def run(self) -> None:
        try:
            summary = self.engine.run()
        except Exception as exc:
            self.scan_failed.emit(str(exc))
        else:
            self.scan_finished.emit(summary)

    def cancel(self) -> None:
        """Thread-safe cooperative cancellation request."""

        self.engine.cancel()
