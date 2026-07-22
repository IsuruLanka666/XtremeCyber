"""Tests for the port specification parser."""

from __future__ import annotations

import unittest

from core.exceptions import ValidationError
from core.scanning.ports import parse_port_spec


class PortParserTests(unittest.TestCase):
    def test_single_ports_are_normalized(self) -> None:
        spec = parse_port_spec("443,80,22")
        self.assertEqual(spec.normalized, "22,80,443")
        self.assertEqual(spec.count, 3)

    def test_adjacent_ranges_are_merged(self) -> None:
        spec = parse_port_spec("1-10,11-20,20-25")
        self.assertEqual(spec.normalized, "1-25")
        self.assertEqual(spec.count, 25)

    def test_invalid_port_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            parse_port_spec("0,80")

    def test_reversed_range_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            parse_port_spec("100-50")


if __name__ == "__main__":
    unittest.main()
