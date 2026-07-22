"""Core data models used by the XtremeCyber scanning subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from core.scanning.ports import PortSpec


class TargetKind(StrEnum):
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    HOSTNAME = "hostname"
    NETWORK = "network"


class ScanProfile(StrEnum):
    QUICK = "quick"
    STANDARD = "standard"
    WEB = "web"
    FULL = "full"
    CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class TargetSpec:
    raw_value: str
    normalized_value: str
    kind: TargetKind
    hosts: tuple[str, ...]

    @property
    def host_count(self) -> int:
        return len(self.hosts)


@dataclass(frozen=True, slots=True)
class ScanConfiguration:
    target: TargetSpec
    ports: PortSpec
    profile: ScanProfile
    max_workers: int
    timeout_seconds: float
    banner_grab: bool
    resolve_hostname: bool
    authorization_confirmed: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target.normalized_value,
            "target_kind": self.target.kind.value,
            "hosts": list(self.target.hosts),
            "host_count": self.target.host_count,
            "port_spec": self.ports.normalized,
            "port_count": self.ports.count,
            "profile": self.profile.value,
            "max_workers": self.max_workers,
            "timeout_seconds": self.timeout_seconds,
            "banner_grab": self.banner_grab,
            "resolve_hostname": self.resolve_hostname,
            "authorization_confirmed": self.authorization_confirmed,
            "created_at": self.created_at.isoformat(),
        }
    