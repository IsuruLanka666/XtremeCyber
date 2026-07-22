"""Tests for target parsing and normalization."""

from __future__ import annotations

import unittest

from core.exceptions import ValidationError
from core.scanning.models import TargetKind
from core.scanning.targets import parse_target


class TargetParserTests(unittest.TestCase):
    def test_ipv4_address(self) -> None:
        target = parse_target("192.168.1.10")
        self.assertEqual(target.kind, TargetKind.IPV4)
        self.assertEqual(target.normalized_value, "192.168.1.10")

    def test_hostname_normalization(self) -> None:
        target = parse_target("Example.COM.")
        self.assertEqual(target.kind, TargetKind.HOSTNAME)
        self.assertEqual(target.normalized_value, "example.com")

    def test_small_network(self) -> None:
        target = parse_target("192.168.1.0/30", max_network_hosts=8)
        self.assertEqual(target.kind, TargetKind.NETWORK)
        self.assertEqual(target.host_count, 2)

    def test_url_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            parse_target("https://example.com")

    def test_large_network_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            parse_target("10.0.0.0/8", max_network_hosts=256)


if __name__ == "__main__":
    unittest.main()
