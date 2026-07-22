"""
Result and progress models for TCP scanning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class PortState(StrEnum):
    """Outcome of a TCP connection attempt."""

    OPEN = "open"
    CLOSED = "closed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class PortScanResult:
    """Result of testing one TCP port on one host."""

    host: str
    port: int
    state: PortState
    service: str = "unknown"
    banner: str = ""
    latency_ms: float | None = None
    error: str = ""
    resolved_address: str = ""
    scanned_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "host": self.host,
            "resolved_address": self.resolved_address,
            "port": self.port,
            "state": self.state.value,
            "service": self.service,
            "banner": self.banner,
            "latency_ms": self.latency_ms,
            "error": self.error,
            "scanned_at": self.scanned_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class ScanProgress:
    """Thread-safe progress snapshot emitted by the engine."""

    completed: int
    total: int
    open_ports: int
    closed_ports: int
    errors: int
    cancelled: bool = False

    @property
    def percentage(self) -> int:
        if self.total <= 0:
            return 0

        return min(100, int((self.completed / self.total) * 100))


@dataclass(frozen=True, slots=True)
class ScanSummary:
    """Final summary for a completed or cancelled scan."""

    total: int
    completed: int
    open_ports: int
    closed_ports: int
    errors: int
    cancelled: bool
    duration_seconds: float

    @property
    def completion_percentage(self) -> int:
        if self.total <= 0:
            return 0

        return min(100, int((self.completed / self.total) * 100))
