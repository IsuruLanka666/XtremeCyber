from __future__ import annotations
import unittest
from core.vulnerability.nvd_parsing import parse_cve_records

SAMPLE = {"vulnerabilities": [{"cve": {"id": "CVE-2099-0001", "sourceIdentifier": "test", "published": "2099-01-01", "lastModified": "2099-01-02", "vulnStatus": "Analyzed", "descriptions": [{"lang": "en", "value": "Example."}], "metrics": {"cvssMetricV31": [{"type": "Primary", "cvssData": {"version": "3.1", "vectorString": "CVSS:3.1/AV:N", "baseScore": 9.8, "baseSeverity": "CRITICAL"}}]}, "weaknesses": [{"description": [{"lang": "en", "value": "CWE-79"}]}], "references": [{"url": "https://example.test"}], "cisaExploitAdd": "2099-01-03"}}]}

class NvdParsingTests(unittest.TestCase):
    def test_parse(self):
        record = parse_cve_records(SAMPLE)[0]
        self.assertEqual(record.cvss_score, 9.8); self.assertEqual(record.severity, "critical"); self.assertTrue(record.known_exploited)
    def test_rejected(self):
        response = {"vulnerabilities": [{"cve": {"id": "CVE-2099-2", "vulnStatus": "Rejected"}}]}
        self.assertEqual(parse_cve_records(response), ())
if __name__ == "__main__": unittest.main()
