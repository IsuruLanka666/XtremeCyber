"""
Authenticated user session model.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from core.auth.permissions import Permission, has_permission


@dataclass(frozen=True, slots=True)
class UserSession:
    """Immutable authenticated user session."""

    user_id: int
    username: str
    email: str | None
    role: str
    login_time: datetime

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_analyst(self) -> bool:
        return self.role in {"admin", "analyst"}

    @property
    def display_role(self) -> str:
        return self.role.replace("_", " ").title()

    def can(self, permission: Permission) -> bool:
        """Check whether this session has a permission."""

        return has_permission(self.role, permission)

    def with_email(self, email: str | None) -> "UserSession":
        """Return a copy of the session with an updated email."""

        return replace(self, email=email)
