"""
Analyze one saved XtremeCyber scan from the command line.

Run from the project root:

    python scripts\\analyze_scan.py 12
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from core.database.database import database_manager
from core.helpers import ensure_directories
from core.vulnerability.service import (
    VulnerabilityAssessmentService,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate service fingerprints and exposure findings "
            "for a saved XtremeCyber scan."
        )
    )
    parser.add_argument(
        "scan_id",
        type=int,
        help="Saved network scan ID",
    )
    arguments = parser.parse_args()

    ensure_directories()
    database_manager.initialize()

    summary = VulnerabilityAssessmentService().analyze_scan(
        arguments.scan_id
    )

    print(f"Scan ID: {summary.scan_id}")
    print(f"Fingerprints: {summary.fingerprints}")
    print(f"Findings: {summary.findings}")
    print(f"Critical: {summary.critical}")
    print(f"High: {summary.high}")
    print(f"Medium: {summary.medium}")
    print(f"Low: {summary.low}")
    print(f"Informational: {summary.info}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
