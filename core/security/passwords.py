"""
Password hashing and verification utilities.
"""

from __future__ import annotations

import bcrypt

from core.exceptions import ValidationError


MINIMUM_PASSWORD_LENGTH = 10


def validate_password_strength(password: str) -> None:
    """Validate the minimum XtremeCyber password policy."""

    if len(password) < MINIMUM_PASSWORD_LENGTH:
        raise ValidationError(
            f"Password must contain at least {MINIMUM_PASSWORD_LENGTH} characters."
        )

    if not any(character.isupper() for character in password):
        raise ValidationError("Password must contain an uppercase letter.")

    if not any(character.islower() for character in password):
        raise ValidationError("Password must contain a lowercase letter.")

    if not any(character.isdigit() for character in password):
        raise ValidationError("Password must contain a number.")

    if not any(not character.isalnum() for character in password):
        raise ValidationError("Password must contain a special character.")


def hash_password(password: str) -> str:
    """Return a bcrypt password hash."""

    validate_password_strength(password)

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12),
    )

    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a stored bcrypt hash."""

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (TypeError, ValueError):
        return False
