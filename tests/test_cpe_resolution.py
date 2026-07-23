from __future__ import annotations
import unittest
from core.vulnerability.cpe import CpeCandidate, parse_cpe23, resolve_product_identity, select_cpe_candidate

class CpeResolutionTests(unittest.TestCase):
    def test_parse(self):
        parts = parse_cpe23("cpe:2.3:a:openbsd:openssh:9.6p1:*:*:*:*:*:*:*")
        self.assertEqual(len(parts), 13); self.assertEqual(parts[4], "openssh")
    def test_select_openssh(self):
        identity = resolve_product_identity("OpenSSH")
        candidate = CpeCandidate("cpe:2.3:a:openbsd:openssh:9.5:*:*:*:*:*:*:*", "OpenBSD OpenSSH 9.5", False, "a", "openbsd", "openssh", "9.5")
        result = select_cpe_candidate(identity, (candidate,), "9.6p1")
        self.assertTrue(result.matched); self.assertIn(":9.6p1:", result.cpe_name)
    def test_unknown(self):
        self.assertIsNone(resolve_product_identity("Unknown service"))
if __name__ == "__main__": unittest.main()
