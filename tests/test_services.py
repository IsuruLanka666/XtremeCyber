"""
Tests for service-name and banner helpers.
"""

from __future__ import annotations

import unittest

from core.scanning.services import sanitize_banner, service_name


class ServiceHelperTests(unittest.TestCase):
    def test_common_service(self) -> None:
        self.assertEqual(service_name(22), "ssh")

    def test_banner_is_flattened_and_sanitized(self) -> None:
        banner = sanitize_banner(
            b"HTTP/1.1 200 OK\r\nServer: Test\x00Server\r\n"
        )

        self.assertEqual(
            banner,
            "HTTP/1.1 200 OK Server: Test Server",
        )


if __name__ == "__main__":
    unittest.main()
