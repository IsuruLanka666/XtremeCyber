"""
Authentication, role management, and account-security service.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from core.auth.permissions import Permission
from core.auth.session import UserSession
from core.auth.user_repository import UserRepository
from core.exceptions import AuthenticationError, ValidationError
from core.logger import get_logger
from core.security.passwords import hash_password, verify_password


logger = get_logger(__name__)

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
)
VALID_ROLES = {"admin", "analyst", "viewer"}


class AuthenticationService:
    """Provide login, RBAC, and account-management operations."""

    def __init__(
        self,
        user_repository: UserRepository | None = None,
    ) -> None:
        self.user_repository = user_repository or UserRepository()

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> UserSession:
        user = self.user_repository.get_by_username(username)

        if user is None or not verify_password(
            password,
            str(user["password_hash"]),
        ):
            logger.warning(
                "Failed login attempt for username '%s'.",
                username.strip(),
            )
            raise AuthenticationError("Invalid username or password.")

        if not bool(user["is_active"]):
            logger.warning(
                "Disabled account attempted login: user_id=%s.",
                user["id"],
            )
            raise AuthenticationError(
                "This user account has been disabled."
            )

        user_id = int(user["id"])
        self.user_repository.update_last_login(user_id)

        session = UserSession(
            user_id=user_id,
            username=str(user["username"]),
            email=str(user["email"]) if user["email"] else None,
            role=str(user["role"]),
            login_time=datetime.now(timezone.utc),
        )

        logger.info(
            "User authenticated: user_id=%s role=%s.",
            session.user_id,
            session.role,
        )

        return session

    def validate_session(
        self,
        session: UserSession,
    ) -> UserSession:
        """Confirm the account remains active and refresh role/email."""

        user = self.user_repository.get_by_id(session.user_id)

        if user is None:
            raise AuthenticationError(
                "The signed-in user account no longer exists."
            )

        if not bool(user["is_active"]):
            raise AuthenticationError(
                "This account has been disabled. Sign in again."
            )

        return UserSession(
            user_id=int(user["id"]),
            username=str(user["username"]),
            email=str(user["email"]) if user["email"] else None,
            role=str(user["role"]),
            login_time=session.login_time,
        )

    @staticmethod
    def require_permission(
        session: UserSession,
        permission: Permission,
    ) -> None:
        if not session.can(permission):
            raise AuthenticationError(
                "Your account does not have permission to perform this action."
            )

    def create_user(
        self,
        username: str,
        password: str,
        email: str | None = None,
        role: str = "viewer",
    ) -> int:
        normalized_username = self._validate_username(username)
        normalized_email = self._validate_email(email)
        normalized_role = self._validate_role(role)

        if self.user_repository.username_exists(normalized_username):
            raise ValidationError("That username already exists.")

        if (
            normalized_email
            and self.user_repository.email_exists(normalized_email)
        ):
            raise ValidationError(
                "That email address is already assigned to another account."
            )

        user_id = self.user_repository.create_user(
            username=normalized_username,
            password_hash=hash_password(password),
            email=normalized_email,
            role=normalized_role,
        )

        logger.info(
            "User created: user_id=%s role=%s.",
            user_id,
            normalized_role,
        )

        return user_id

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

        return self.create_user(
            username=username,
            password=password,
            email=email,
            role="admin",
        )

    def create_user_as_admin(
        self,
        session: UserSession,
        username: str,
        password: str,
        email: str | None,
        role: str,
    ) -> int:
        self.require_permission(session, Permission.MANAGE_USERS)
        return self.create_user(username, password, email, role)

    def list_users_as_admin(
        self,
        session: UserSession,
    ) -> list[dict]:
        self.require_permission(session, Permission.MANAGE_USERS)
        return self.user_repository.list_users()

    def update_user_role_as_admin(
        self,
        session: UserSession,
        user_id: int,
        role: str,
    ) -> None:
        self.require_permission(session, Permission.MANAGE_USERS)
        normalized_role = self._validate_role(role)
        user = self._get_required_user(user_id)

        if user_id == session.user_id:
            raise ValidationError(
                "You cannot change your own role while signed in."
            )

        if (
            str(user["role"]) == "admin"
            and normalized_role != "admin"
            and bool(user["is_active"])
            and self.user_repository.count_active_admins() <= 1
        ):
            raise ValidationError(
                "The final active administrator cannot be demoted."
            )

        self.user_repository.update_role(user_id, normalized_role)

        logger.info(
            "User role changed by admin_id=%s: user_id=%s role=%s.",
            session.user_id,
            user_id,
            normalized_role,
        )

    def set_user_active_as_admin(
        self,
        session: UserSession,
        user_id: int,
        is_active: bool,
    ) -> None:
        self.require_permission(session, Permission.MANAGE_USERS)
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

        logger.info(
            "User status changed by admin_id=%s: user_id=%s active=%s.",
            session.user_id,
            user_id,
            is_active,
        )

    def reset_user_password_as_admin(
        self,
        session: UserSession,
        user_id: int,
        new_password: str,
    ) -> None:
        self.require_permission(session, Permission.MANAGE_USERS)
        self._get_required_user(user_id)

        self.user_repository.update_password(
            user_id,
            hash_password(new_password),
        )

        logger.info(
            "User password reset by admin_id=%s: user_id=%s.",
            session.user_id,
            user_id,
        )

    def update_user_email_as_admin(
        self,
        session: UserSession,
        user_id: int,
        email: str | None,
    ) -> None:
        self.require_permission(session, Permission.MANAGE_USERS)
        self._get_required_user(user_id)

        normalized_email = self._validate_email(email)

        if (
            normalized_email
            and self.user_repository.email_exists(
                normalized_email,
                excluding_user_id=user_id,
            )
        ):
            raise ValidationError(
                "That email address is already assigned to another account."
            )

        self.user_repository.update_profile(user_id, normalized_email)

    def change_own_password(
        self,
        session: UserSession,
        current_password: str,
        new_password: str,
    ) -> None:
        self.require_permission(
            session,
            Permission.MANAGE_OWN_ACCOUNT,
        )

        user = self._get_required_user(session.user_id)

        if not verify_password(
            current_password,
            str(user["password_hash"]),
        ):
            raise AuthenticationError(
                "The current password is incorrect."
            )

        if verify_password(
            new_password,
            str(user["password_hash"]),
        ):
            raise ValidationError(
                "The new password must be different from the current password."
            )

        self.user_repository.update_password(
            session.user_id,
            hash_password(new_password),
        )

        logger.info(
            "User changed own password: user_id=%s.",
            session.user_id,
        )

    def update_own_email(
        self,
        session: UserSession,
        email: str | None,
    ) -> UserSession:
        self.require_permission(
            session,
            Permission.MANAGE_OWN_ACCOUNT,
        )

        normalized_email = self._validate_email(email)

        if (
            normalized_email
            and self.user_repository.email_exists(
                normalized_email,
                excluding_user_id=session.user_id,
            )
        ):
            raise ValidationError(
                "That email address is already assigned to another account."
            )

        self.user_repository.update_profile(
            session.user_id,
            normalized_email,
        )

        logger.info(
            "User updated own email: user_id=%s.",
            session.user_id,
        )

        return session.with_email(normalized_email)

    def _get_required_user(self, user_id: int) -> dict:
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise ValidationError("The selected user no longer exists.")

        return user

    @staticmethod
    def _validate_username(username: str) -> str:
        normalized = username.strip()

        if not USERNAME_PATTERN.fullmatch(normalized):
            raise ValidationError(
                "Username must be 3-32 characters and may contain "
                "letters, numbers, dots, underscores, and hyphens."
            )

        return normalized

    @staticmethod
    def _validate_email(email: str | None) -> str | None:
        if email is None or not email.strip():
            return None

        normalized = email.strip().lower()

        if not EMAIL_PATTERN.fullmatch(normalized):
            raise ValidationError("Enter a valid email address.")

        return normalized

    @staticmethod
    def _validate_role(role: str) -> str:
        normalized = role.strip().lower()

        if normalized not in VALID_ROLES:
            raise ValidationError("Invalid user role.")

        return normalized
