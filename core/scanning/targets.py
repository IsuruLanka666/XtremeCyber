"""Target validation, normalization, and optional DNS resolution."""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass

from core.exceptions import ValidationError
from core.scanning.models import TargetKind, TargetSpec

_HOSTNAME_LABEL = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")


@dataclass(frozen=True, slots=True)
class ResolvedTarget:
    target: TargetSpec
    addresses: tuple[str, ...]


def parse_target(value: str, *, max_network_hosts: int = 256) -> TargetSpec:
    """Validate an IPv4, IPv6, hostname, or CIDR target."""

    raw_value = value
    text = value.strip()

    if not text:
        raise ValidationError("Enter a target hostname, IP address, or CIDR.")
    if "://" in text:
        raise ValidationError("Enter only the hostname or IP address, not a full URL.")
    if any(character.isspace() for character in text):
        raise ValidationError("The target cannot contain spaces.")

    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]

    if "/" in text:
        return _parse_network(raw_value, text, max_network_hosts)

    try:
        address = ipaddress.ip_address(text)
    except ValueError:
        return _parse_hostname(raw_value, text)

    kind = TargetKind.IPV4 if isinstance(address, ipaddress.IPv4Address) else TargetKind.IPV6
    normalized = str(address)

    return TargetSpec(raw_value, normalized, kind, (normalized,))


def resolve_target(target: TargetSpec) -> ResolvedTarget:
    """Resolve a hostname to unique IP addresses."""

    if target.kind != TargetKind.HOSTNAME:
        return ResolvedTarget(target, target.hosts)

    try:
        results = socket.getaddrinfo(
            target.normalized_value,
            None,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise ValidationError(
            f"Could not resolve hostname '{target.normalized_value}'."
        ) from exc

    addresses = tuple(sorted({str(result[4][0]) for result in results if result[4]}))
    if not addresses:
        raise ValidationError(
            f"No network addresses were found for '{target.normalized_value}'."
        )

    return ResolvedTarget(target, addresses)


def _parse_network(raw_value: str, value: str, max_network_hosts: int) -> TargetSpec:
    try:
        network = ipaddress.ip_network(value, strict=False)
    except ValueError as exc:
        raise ValidationError(f"'{value}' is not a valid CIDR network.") from exc

    if max_network_hosts < 1:
        raise ValidationError("The maximum network host limit must be positive.")

    hosts = tuple(str(host) for host in network.hosts())
    if not hosts and network.num_addresses == 1:
        hosts = (str(network.network_address),)

    if len(hosts) > max_network_hosts:
        raise ValidationError(
            f"The network contains {len(hosts)} usable hosts. "
            f"The current safety limit is {max_network_hosts}."
        )

    return TargetSpec(raw_value, str(network), TargetKind.NETWORK, hosts)


def _parse_hostname(raw_value: str, value: str) -> TargetSpec:
    hostname = value.rstrip(".").lower()

    if not hostname:
        raise ValidationError("Enter a valid hostname.")
    if len(hostname) > 253:
        raise ValidationError("A hostname cannot exceed 253 characters.")

    labels = hostname.split(".")
    if not all(_HOSTNAME_LABEL.fullmatch(label) for label in labels):
        raise ValidationError(f"'{value}' is not a valid hostname.")

    return TargetSpec(raw_value, hostname, TargetKind.HOSTNAME, (hostname,))
