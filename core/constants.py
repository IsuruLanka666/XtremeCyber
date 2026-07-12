"""
Constants and enumerations used on XtremeCyber.
"""

from enum import Enum


DATABASE_SCHEMA_VERSION = 1


class Theme(str, Enum):
    DARK = "dark"
    LIGHT = "light"


class ScanType(str, Enum):
    QUICK = "quick"
    FULL = "full"
    WEB = "web"
    SSL = "ssl"
    CUSTOM = "custom"


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HostStatus(str, Enum):
    UNKNOWN = "unknown"
    ONLINE = "online"
    OFFLINE = "offline"


class PortState(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


SEVERITY_ORDER = {
    Severity.INFORMATIONAL.value: 0,
    Severity.LOW.value: 1,
    Severity.MEDIUM.value: 2,
    Severity.HIGH.value: 3,
    Severity.CRITICAL.value: 4,
}


DEFAULT_SETTINGS = {
    "theme": Theme.DARK.value,
    "scan_timeout": "3",
    "max_threads": "100",
    "default_port_range": "1-1000",
    "email_alerts_enabled": "false",
}