"""
Authentication and account service.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from core.auth.session import UserSession
from core.auth.user_repository import UserRepository
from core.exceptions import AuthenticationError, ValidationError
from core.security.passwords import hash_password, verify_password


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
VALID_ROLES = {"admin", "analyst", "viewer"}


class AuthenticationService:
    """Provide authentication and user creation operations."""

    def __init__(
        self,
        user_repository: UserRepository | None = None,
    ) -> None:
        self.user_repository = user_repository or UserRepository()

    def create_user(
        self,
        username: str,
        password: str,
        email: str | None = None,
        role: str = "viewer",
    ) -> int:
        normalized_username = username.strip()
        normalized_role = role.strip().lower()

        if not USERNAME_PATTERN.fullmatch(normalized_username):
            raise ValidationError(
                "Username must be 3-32 characters and may contain "
                "letters, numbers, dots, underscores, and hyphens."
            )

        if normalized_role not in VALID_ROLES:
            raise ValidationError("Invalid user role.")

        if self.user_repository.username_exists(normalized_username):
            raise ValidationError("That username already exists.")

        return self.user_repository.create_user(
            username=normalized_username,
            password_hash=hash_password(password),
            email=email,
            role=normalized_role,
        )

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> UserSession:
        user = self.user_repository.get_by_username(username)

        if user is None:
            raise AuthenticationError("Invalid username or password.")

        if not bool(user["is_active"]):
            raise AuthenticationError(
                "This user account has been disabled."
            )

        if not verify_password(password, str(user["password_hash"])):
            raise AuthenticationError("Invalid username or password.")

        user_id = int(user["id"])
        self.user_repository.update_last_login(user_id)

        return UserSession(
            user_id=user_id,
            username=str(user["username"]),
            email=str(user["email"]) if user["email"] else None,
            role=str(user["role"]),
            login_time=datetime.now(timezone.utc),
        )

    def create_initial_admin(
        self,
        username: str,
        password: str,
        email: str | None = None,
    ) -> int:
        if self.user_repository.count_users() > 0:
            raise ValidationError(
                "An account already exists. Initial administrator creation "
                "is only available for an empty user table."
            )

        return self.create_user(
            username=username,
            password=password,
            email=email,
            role="admin",
        )
