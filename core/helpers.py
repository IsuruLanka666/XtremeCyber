"""
General helper and validation functions for XtremeCyber.
"""

from __future__ import annotations

import ipaddress
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from config import (
    ASSETS_DIR,
    DATABASE_DIR,
    EXPORT_DIR,
    LOG_DIR,
    MAX_PORT,
    MIN_PORT,
    SCREENSHOT_DIR,
)
from core.exceptions import InvalidPortRangeError, InvalidTargetError


HOSTNAME_PATTERN = re.compile(
    r"^(?=.{1,253}$)"
    r"(?:"
    r"(?!-)[A-Za-z0-9-]{1,63}(?<!-)\."
    r")*"
    r"(?!-)[A-Za-z0-9-]{1,63}(?<!-)$"
)


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""

    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""

    return utc_now().isoformat(timespec="seconds")


def ensure_directories(
    directories: Iterable[Path] | None = None,
) -> None:
    """
    Create all required application directories.

    Args:
        directories: Optional custom directory collection.
    """

    required_directories = directories or (
        ASSETS_DIR,
        DATABASE_DIR,
        EXPORT_DIR,
        LOG_DIR,
        SCREENSHOT_DIR,
    )

    for directory in required_directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def validate_target(target: str) -> str:
    """
    Validate an IPv4 address, IPv6 address, or hostname.

    URLs like https://example.com are intentionally rejected because
    scanners should receive the host separately from the protocol.

    Args:
        target: User-supplied target.

    Returns:
        The normalized target.

    Raises:
        InvalidTargetError: If the target is invalid.
    """

    normalized = target.strip()

    if not normalized:
        raise InvalidTargetError("A target is required.")

    if "://" in normalized:
        raise InvalidTargetError(
            "Enter only an IP address or hostname, without http:// or https://."
        )

    if "/" in normalized:
        try:
            network = ipaddress.ip_network(normalized, strict=False)
            return str(network)
        except ValueError as exc:
            raise InvalidTargetError(
                f"Invalid network target: {normalized}"
            ) from exc

    try:
        address = ipaddress.ip_address(normalized)
        return str(address)
    except ValueError:
        pass

    if not HOSTNAME_PATTERN.fullmatch(normalized):
        raise InvalidTargetError(
            f"Invalid IP address or hostname: {normalized}"
        )

    return normalized.lower()


def parse_port_range(port_range: str) -> list[int]:
    """
    Takes a string of ports (e.g., '80,443' or '1-1000') and returns a sorted list of integers.
    
    Raises ValueError if the input format is broken.
    """

    value = port_range.strip()

    if not value:
        raise InvalidPortRangeError("A port range is required.")

    ports: set[int] = set()

    for section in value.split(","):
        section = section.strip()

        if not section:
            raise InvalidPortRangeError(
                "The port range contains an empty section."
            )

        if "-" in section:
            parts = section.split("-")

            if len(parts) != 2:
                raise InvalidPortRangeError(
                    f"Invalid port range section: {section}"
                )

            try:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
            except ValueError as exc:
                raise InvalidPortRangeError(
                    f"Port values must be numbers: {section}"
                ) from exc

            _validate_port(start)
            _validate_port(end)

            if start > end:
                raise InvalidPortRangeError(
                    f"Range start cannot exceed range end: {section}"
                )

            ports.update(range(start, end + 1))
        else:
            try:
                port = int(section)
            except ValueError as exc:
                raise InvalidPortRangeError(
                    f"Invalid port number: {section}"
                ) from exc

            _validate_port(port)
            ports.add(port)

    return sorted(ports)


def _validate_port(port: int) -> None:
    """Validate a single TCP or UDP port number."""

    if port < MIN_PORT or port > MAX_PORT:
        raise InvalidPortRangeError(
            f"Port {port} is outside the valid range "
            f"{MIN_PORT}-{MAX_PORT}."
        )


def format_duration(seconds: float) -> str:
    """Format a duration into a human-readable value."""

    if seconds < 0:
        seconds = 0

    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, remaining_seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}h {minutes}m {remaining_seconds}s"

    if minutes:
        return f"{minutes}m {remaining_seconds}s"

    return f"{remaining_seconds}s"