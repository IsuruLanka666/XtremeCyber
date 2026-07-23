from __future__ import annotations
import unittest
from core.vulnerability.intelligence_service import VulnerabilityIntelligenceService

class FakeRepository:
    def __init__(self): self.matches=[]
    def get_fingerprints(self, scan_id): return [{"id": 7, "product": "OpenSSH", "version": "9.6p1"}]
    def clear_scan_matches(self, scan_id): pass
    def get_cpe_resolution(self, *a, **k): return None
    def save_cpe_resolution(self, value): self.resolution=value
    def get_cached_cves_for_cpe(self, *a, **k): return None
    def save_cves_for_cpe(self, cpe, records): self.records=records
    def replace_fingerprint_matches(self, **kwargs): self.matches.append(kwargs)

class FakeClient:
    def __init__(self): self.request_count=0
    def search_cpes(self, keyword, results_per_page=100):
        self.request_count += 1
        return {"products": [{"cpe": {"deprecated": False, "cpeName": "cpe:2.3:a:openbsd:openssh:9.5:*:*:*:*:*:*:*", "titles": [{"lang": "en", "title": "OpenBSD OpenSSH 9.5"}]}}]}
    def cves_for_cpe(self, cpe_name, results_per_page=2000):
        self.request_count += 1
        return {"vulnerabilities": [{"cve": {"id": "CVE-2099-0001", "vulnStatus": "Analyzed", "descriptions": [{"lang": "en", "value": "Example"}], "metrics": {"cvssMetricV31": [{"type": "Primary", "cvssData": {"version": "3.1", "baseScore": 7.5, "baseSeverity": "HIGH", "vectorString": "CVSS:3.1/AV:N"}}]}}}]}

class ServiceTests(unittest.TestCase):
    def test_correlate(self):
        repo=FakeRepository(); service=VulnerabilityIntelligenceService(repository=repo, nvd_client=FakeClient())
        summary=service.correlate_scan(3)
        self.assertEqual(summary.fingerprints_matched, 1); self.assertEqual(summary.cves_matched, 1); self.assertEqual(summary.high, 1)
if __name__ == "__main__": unittest.main()
