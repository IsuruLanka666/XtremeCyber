"""
Tests for service fingerprinting.
"""

from __future__ import annotations

import unittest

from core.scanning.results import PortScanResult, PortState
from core.vulnerability.fingerprinting import fingerprint_result
from core.vulnerability.models import Confidence


class FingerprintingTests(unittest.TestCase):
    def test_openssh_banner(self) -> None:
        fingerprint = fingerprint_result(
            PortScanResult(
                host="127.0.0.1",
                resolved_address="127.0.0.1",
                port=22,
                state=PortState.OPEN,
                service="ssh",
                banner="SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13",
            )
        )

        self.assertIsNotNone(fingerprint)
        self.assertEqual(fingerprint.product, "OpenSSH")
        self.assertEqual(fingerprint.version, "9.6p1")
        self.assertEqual(fingerprint.confidence, Confidence.HIGH)

    def test_nginx_http_banner(self) -> None:
        fingerprint = fingerprint_result(
            PortScanResult(
                host="example.test",
                resolved_address="127.0.0.1",
                port=80,
                state=PortState.OPEN,
                service="http",
                banner=(
                    "HTTP/1.1 200 OK Server: nginx/1.24.0 "
                    "Content-Type: text/html"
                ),
            )
        )

        self.assertEqual(fingerprint.product, "nginx")
        self.assertEqual(fingerprint.version, "1.24.0")

    def test_closed_port_has_no_fingerprint(self) -> None:
        fingerprint = fingerprint_result(
            PortScanResult(
                host="127.0.0.1",
                port=23,
                state=PortState.CLOSED,
                service="telnet",
            )
        )

        self.assertIsNone(fingerprint)


if __name__ == "__main__":
    unittest.main()
