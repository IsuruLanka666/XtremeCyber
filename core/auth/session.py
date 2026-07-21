"""
Authenticated user session model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


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
