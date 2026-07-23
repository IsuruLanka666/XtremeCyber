"""Correlate one saved scan with NVD CPE/CVE data."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from core.database.database import database_manager
from core.helpers import ensure_directories
from core.vulnerability.intelligence_service import VulnerabilityIntelligenceService

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("scan_id", type=int); parser.add_argument("--force", action="store_true"); args = parser.parse_args()
    ensure_directories(); database_manager.initialize()
    s = VulnerabilityIntelligenceService().correlate_scan(args.scan_id, force_refresh=args.force)
    for label, value in (("Scan ID", s.scan_id), ("Fingerprints considered", s.fingerprints_considered), ("Fingerprints matched to CPE", s.fingerprints_matched), ("Skipped without product", s.skipped_no_product), ("Skipped without version", s.skipped_no_version), ("Ambiguous products", s.ambiguous_products), ("Unique CVEs", s.cves_matched), ("Critical", s.critical), ("High", s.high), ("Medium", s.medium), ("Low", s.low), ("Unknown severity", s.unknown), ("Known exploited", s.known_exploited), ("Cache hits", s.cache_hits), ("NVD API requests", s.api_requests)):
        print(f"{label}: {value}")
    if s.errors:
        print("Errors:"); [print(f"  - {x}") for x in s.errors]
    return 0 if not s.errors else 2
if __name__ == "__main__": raise SystemExit(main())
