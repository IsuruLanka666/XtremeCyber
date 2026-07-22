"""Built-in XtremeCyber TCP scan profiles."""

from __future__ import annotations

from core.exceptions import ValidationError
from core.scanning.models import ScanProfile
from core.scanning.ports import PortSpec, parse_port_spec

PROFILE_LABELS: dict[ScanProfile, str] = {
    ScanProfile.QUICK: "Quick — common services",
    ScanProfile.STANDARD: "Standard — ports 1-1024",
    ScanProfile.WEB: "Web services",
    ScanProfile.FULL: "Full TCP — ports 1-65535",
    ScanProfile.CUSTOM: "Custom port selection",
}

_PROFILE_PORTS: dict[ScanProfile, str] = {
    ScanProfile.QUICK: (
        "20-23,25,53,67-69,80,110,123,135,137-139,143,161-162,"
        "389,443,445,465,514,587,631,636,993,995,1433,1521,2049,"
        "3306,3389,5432,5900,6379,8080,8443"
    ),
    ScanProfile.STANDARD: "1-1024",
    ScanProfile.WEB: (
        "80,443,3000,4000,5000,7001,8000,8008,8080,8081,8443,"
        "8888,9000,9090,9443"
    ),
    ScanProfile.FULL: "1-65535",
}


def ports_for_profile(profile: ScanProfile, custom_value: str = "") -> PortSpec:
    if profile == ScanProfile.CUSTOM:
        if not custom_value.strip():
            raise ValidationError("Enter a custom TCP port specification.")
        return parse_port_spec(custom_value)

    return parse_port_spec(_PROFILE_PORTS[profile])
