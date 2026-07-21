"""
Authentication and administrator user-management service.
"""

from __future__ import annotations
import re
from datetime import datetime, timezone

from core.auth.session import UserSession
from core.auth.user_repository import UserRepository
from core.exceptions import AuthenticationError, ValidationError
from core.security.passwords import hash_password, verify_password


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
)
VALID_ROLES = {"admin", "analyst", "viewer"}


class AuthenticationService:
    """Provide login, account creation, and admin management."""

    def __init__(self, user_repository: UserRepository | None = None) -> None:
        self.user_repository = user_repository or UserRepository()

    def create_user(
        self,
        username: str,
        password: str,
        email: str | None = None,
        role: str = "viewer",
    ) -> int:
        username = self._validate_username(username)
        email = self._validate_email(email)
        role = self._validate_role(role)

        if self.user_repository.username_exists(username):
            raise ValidationError("That username already exists.")

        if email and self.user_repository.email_exists(email):
            raise ValidationError(
                "That email address is already assigned to another account."
            )

        return self.user_repository.create_user(
            username=username,
            password_hash=hash_password(password),
            email=email,
            role=role,
        )

    def create_user_as_admin(
        self,
        session: UserSession,
        username: str,
        password: str,
        email: str | None,
        role: str,
    ) -> int:
        self._require_admin(session)
        return self.create_user(username, password, email, role)

    def authenticate(self, username: str, password: str) -> UserSession:
        user = self.user_repository.get_by_username(username)

        if user is None or not verify_password(
            password,
            str(user["password_hash"]),
        ):
            raise AuthenticationError("Invalid username or password.")

        if not bool(user["is_active"]):
            raise AuthenticationError("This user account has been disabled.")

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
                "Initial administrator creation requires an empty user table."
            )
        return self.create_user(username, password, email, "admin")

    def list_users_as_admin(self, session: UserSession) -> list[dict]:
        self._require_admin(session)
        return self.user_repository.list_users()

    def update_user_role_as_admin(
        self,
        session: UserSession,
        user_id: int,
        role: str,
    ) -> None:
        self._require_admin(session)
        role = self._validate_role(role)
        user = self._get_required_user(user_id)

        if user_id == session.user_id:
            raise ValidationError(
                "You cannot change your own role while signed in."
            )

        if (
            str(user["role"]) == "admin"
            and role != "admin"
            and bool(user["is_active"])
            and self.user_repository.count_active_admins() <= 1
        ):
            raise ValidationError(
                "The final active administrator cannot be demoted."
            )

        self.user_repository.update_role(user_id, role)

    def set_user_active_as_admin(
        self,
        session: UserSession,
        user_id: int,
        is_active: bool,
    ) -> None:
        self._require_admin(session)
        user = self._get_required_user(user_id)

        if user_id == session.user_id and not is_active:
            raise ValidationError(
                "You cannot deactivate your own signed-in account."
            )

        if (
            str(user["role"]) == "admin"
            and bool(user["is_active"])
            and not is_active
            and self.user_repository.count_active_admins() <= 1
        ):
            raise ValidationError(
                "The final active administrator cannot be deactivated."
            )

        self.user_repository.set_active(user_id, is_active)

    def reset_user_password_as_admin(
        self,
        session: UserSession,
        user_id: int,
        new_password: str,
    ) -> None:
        self._require_admin(session)
        self._get_required_user(user_id)
        self.user_repository.update_password(
            user_id,
            hash_password(new_password),
        )

    @staticmethod
    def _require_admin(session: UserSession) -> None:
        if not session.is_admin:
            raise AuthenticationError(
                "Administrator permission is required."
            )

    def _get_required_user(self, user_id: int) -> dict:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise ValidationError("The selected user no longer exists.")
        return user

    @staticmethod
    def _validate_username(username: str) -> str:
        username = username.strip()
        if not USERNAME_PATTERN.fullmatch(username):
            raise ValidationError(
                "Username must be 3-32 characters and may contain "
                "letters, numbers, dots, underscores, and hyphens."
            )
        return username

    @staticmethod
    def _validate_email(email: str | None) -> str | None:
        if email is None or not email.strip():
            return None
        email = email.strip().lower()
        if not EMAIL_PATTERN.fullmatch(email):
            raise ValidationError("Enter a valid email address.")
        return email

    @staticmethod
    def _validate_role(role: str) -> str:
        role = role.strip().lower()
        if role not in VALID_ROLES:
            raise ValidationError("Invalid user role.")
        return role
