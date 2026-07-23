"""
Tests for exposure rules.
"""

from __future__ import annotations

import unittest

from core.scanning.results import PortScanResult, PortState
from core.vulnerability.analyzer import VulnerabilityAnalyzer
from core.vulnerability.models import Severity


class ExposureRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = VulnerabilityAnalyzer()

    def test_telnet_is_high_severity(self) -> None:
        analysis = self.analyzer.analyze_result(
            PortScanResult(
                host="127.0.0.1",
                resolved_address="127.0.0.1",
                port=23,
                state=PortState.OPEN,
                service="telnet",
                banner="",
            )
        )

        titles = {finding.title for finding in analysis.findings}
        severities = {
            finding.severity for finding in analysis.findings
        }

        self.assertIn("Telnet service exposed", titles)
        self.assertIn(Severity.HIGH, severities)

    def test_redis_has_database_and_redis_findings(self) -> None:
        analysis = self.analyzer.analyze_result(
            PortScanResult(
                host="127.0.0.1",
                resolved_address="127.0.0.1",
                port=6379,
                state=PortState.OPEN,
                service="redis",
                banner="redis_version:7.2.4",
            )
        )

        rule_ids = {
            finding.rule_id for finding in analysis.findings
        }

        self.assertIn("XC-EXPOSURE-006", rule_ids)
        self.assertIn("XC-EXPOSURE-007", rule_ids)
        self.assertIn("XC-DISCLOSURE-001", rule_ids)

    def test_version_disclosure(self) -> None:
        analysis = self.analyzer.analyze_result(
            PortScanResult(
                host="127.0.0.1",
                resolved_address="127.0.0.1",
                port=22,
                state=PortState.OPEN,
                service="ssh",
                banner="SSH-2.0-OpenSSH_9.6p1",
            )
        )

        self.assertTrue(
            any(
                finding.rule_id == "XC-DISCLOSURE-001"
                for finding in analysis.findings
            )
        )


if __name__ == "__main__":
    unittest.main()
