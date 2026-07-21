"""
Role-based permissions for XtremeCyber.
"""

from __future__ import annotations

from enum import Enum


class Permission(str, Enum):
    """Actions that may be granted to a user role."""

    VIEW_DASHBOARD = "view_dashboard"
    RUN_SCAN = "run_scan"
    VIEW_RESULTS = "view_results"
    VIEW_REPORTS = "view_reports"
    GENERATE_REPORTS = "generate_reports"
    MANAGE_APPLICATION = "manage_application"
    MANAGE_USERS = "manage_users"
    MANAGE_OWN_ACCOUNT = "manage_own_account"


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "admin": frozenset(Permission),
    "analyst": frozenset(
        {
            Permission.VIEW_DASHBOARD,
            Permission.RUN_SCAN,
            Permission.VIEW_RESULTS,
            Permission.VIEW_REPORTS,
            Permission.GENERATE_REPORTS,
            Permission.MANAGE_OWN_ACCOUNT,
        }
    ),
    "viewer": frozenset(
        {
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_RESULTS,
            Permission.VIEW_REPORTS,
            Permission.MANAGE_OWN_ACCOUNT,
        }
    ),
}


def permissions_for_role(role: str) -> frozenset[Permission]:
    """Return the permissions assigned to a role."""

    return ROLE_PERMISSIONS.get(role.strip().lower(), frozenset())


def has_permission(role: str, permission: Permission) -> bool:
    """Return whether a role includes a permission."""

    return permission in permissions_for_role(role)
