"""Scan configuration validation service."""

from __future__ import annotations

from core.exceptions import ValidationError
from core.scanning.models import ScanConfiguration, ScanProfile
from core.scanning.profiles import ports_for_profile
from core.scanning.targets import parse_target


def build_scan_configuration(
    *,
    target_value: str,
    profile: ScanProfile,
    custom_ports: str,
    max_workers: int,
    timeout_seconds: float,
    banner_grab: bool,
    resolve_hostname: bool,
    authorization_confirmed: bool,
    worker_limit: int = 200,
    max_network_hosts: int = 256,
) -> ScanConfiguration:
    """Validate user input and return an immutable scan configuration."""

    if not authorization_confirmed:
        raise ValidationError(
            "Confirm that you are authorized to assess the target."
        )
    if not 1 <= max_workers <= worker_limit:
        raise ValidationError(
            f"Worker count must be between 1 and {worker_limit}."
        )
    if not 0.1 <= timeout_seconds <= 30.0:
        raise ValidationError(
            "Connection timeout must be between 0.1 and 30 seconds."
        )

    target = parse_target(target_value, max_network_hosts=max_network_hosts)
    ports = ports_for_profile(profile, custom_ports)

    return ScanConfiguration(
        target=target,
        ports=ports,
        profile=profile,
        max_workers=max_workers,
        timeout_seconds=timeout_seconds,
        banner_grab=banner_grab,
        resolve_hostname=resolve_hostname,
        authorization_confirmed=authorization_confirmed,
    )