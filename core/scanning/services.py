"""
Safe service identification and bounded banner collection.
"""

from __future__ import annotations

import re
import socket


_COMMON_SERVICES: dict[int, str] = {
    20: "ftp-data",
    21: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    53: "domain",
    67: "dhcp-server",
    68: "dhcp-client",
    69: "tftp",
    80: "http",
    110: "pop3",
    123: "ntp",
    135: "msrpc",
    137: "netbios-ns",
    138: "netbios-dgm",
    139: "netbios-ssn",
    143: "imap",
    161: "snmp",
    162: "snmptrap",
    389: "ldap",
    443: "https",
    445: "microsoft-ds",
    465: "smtps",
    514: "syslog",
    587: "submission",
    631: "ipp",
    636: "ldaps",
    993: "imaps",
    995: "pop3s",
    1433: "ms-sql-s",
    1521: "oracle",
    2049: "nfs",
    3306: "mysql",
    3389: "ms-wbt-server",
    5432: "postgresql",
    5900: "vnc",
    6379: "redis",
    8000: "http-alt",
    8080: "http-proxy",
    8081: "http-alt",
    8443: "https-alt",
    9000: "cslistener",
    9090: "websm",
    9443: "https-alt",
}

_HTTP_PORTS = {
    80,
    3000,
    4000,
    5000,
    7001,
    8000,
    8008,
    8080,
    8081,
    8888,
    9000,
    9090,
}

_TEXT_CLEANUP = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]+")


def service_name(port: int) -> str:
    """Return a best-effort TCP service name."""

    if port in _COMMON_SERVICES:
        return _COMMON_SERVICES[port]

    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def collect_banner(
    connected_socket: socket.socket,
    *,
    host: str,
    port: int,
    timeout_seconds: float,
    max_bytes: int = 256,
) -> str:
    """
    Perform bounded, non-invasive banner collection.

    The function only reads a greeting or sends a small HTTP HEAD request on
    common clear-text HTTP ports. It does not authenticate, exploit, or modify
    the remote service.
    """

    if max_bytes <= 0:
        return ""

    original_timeout = connected_socket.gettimeout()
    connected_socket.settimeout(min(timeout_seconds, 1.5))

    try:
        if port in _HTTP_PORTS:
            request = (
                f"HEAD / HTTP/1.0\r\n"
                f"Host: {host}\r\n"
                "User-Agent: XtremeCyber/1.0\r\n"
                "Connection: close\r\n\r\n"
            )
            connected_socket.sendall(request.encode("ascii", errors="ignore"))

        data = connected_socket.recv(max_bytes)
    except (TimeoutError, socket.timeout, OSError):
        return ""
    finally:
        connected_socket.settimeout(original_timeout)

    return sanitize_banner(data)


def sanitize_banner(data: bytes) -> str:
    """Convert raw banner bytes into a single safe display line."""

    if not data:
        return ""

    text = data.decode("utf-8", errors="replace")
    text = _TEXT_CLEANUP.sub(" ", text)
    text = " ".join(text.replace("\r", " ").replace("\n", " ").split())

    return text[:256]
