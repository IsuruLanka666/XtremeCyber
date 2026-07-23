"""Check connectivity to the NVD CVE API."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from core.vulnerability.nvd_client import NvdClient
from core.vulnerability.nvd_parsing import parse_cve_records

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--cve", default="CVE-2021-44228"); args = parser.parse_args()
    client = NvdClient(); records = parse_cve_records(client.get_cve(args.cve))
    if not records: print("No matching CVE returned."); return 1
    r = records[0]; print(f"CVE: {r.cve_id}\nStatus: {r.vuln_status}\nCVSS: {r.cvss_score} {r.severity}\nDescription: {r.description[:300]}\nAPI requests: {client.request_count}"); return 0
if __name__ == "__main__": raise SystemExit(main())
