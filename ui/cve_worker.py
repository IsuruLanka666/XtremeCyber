"""Background worker for NVD CVE correlation."""
from __future__ import annotations
from PySide6.QtCore import QObject, Signal, Slot
from core.vulnerability.intelligence_service import VulnerabilityIntelligenceService

class CveCorrelationWorker(QObject):
    status_changed = Signal(str)
    completed = Signal(object)
    failed = Signal(str)
    def __init__(self, scan_id: int, *, force_refresh: bool = False) -> None:
        super().__init__(); self.scan_id = int(scan_id); self.force_refresh = bool(force_refresh)
    @Slot()
    def run(self) -> None:
        self.status_changed.emit(f"Checking NVD intelligence for scan #{self.scan_id}...")
        try:
            summary = VulnerabilityIntelligenceService().correlate_scan(self.scan_id, force_refresh=self.force_refresh)
        except Exception as exc:
            self.failed.emit(str(exc)); return
        self.completed.emit(summary)
