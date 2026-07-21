"""
Self-service account page for XtremeCyber.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.auth.service import AuthenticationService
from core.auth.session import UserSession
from core.exceptions import XtremeCyberError


class AccountPage(QWidget):
    """Allow users to review and secure their own accounts."""

    logout_requested = Signal()

    def __init__(
        self,
        session: UserSession,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.session = session
        self.authentication_service = AuthenticationService()

        self.setObjectName("pageBackground")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 34)
        layout.setSpacing(18)

        title = QLabel("My account")
        title.setObjectName("accentHeading")
        title.setMinimumHeight(52)

        subtitle = QLabel(
            "Review your account, update your email address, "
            "and change your password securely."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        subtitle.setMinimumHeight(42)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        content_row = QHBoxLayout()
        content_row.setSpacing(18)
        content_row.addWidget(self._create_profile_card(), 1)
        content_row.addWidget(self._create_password_card(), 1)

        layout.addLayout(content_row)
        layout.addStretch()

    def _create_profile_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")
        card.setMinimumHeight(380)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Profile")
        title.setObjectName("sectionTitle")

        description = QLabel(
            "Your username and role are managed by an administrator."
        )
        description.setObjectName("sectionSubtitle")
        description.setWordWrap(True)
        description.setMinimumHeight(42)

        form = QFormLayout()
        form.setSpacing(12)

        username_value = QLabel(self.session.username)
        username_value.setObjectName("pageSubtitle")

        role_value = QLabel(self.session.display_role)
        role_value.setObjectName("pageSubtitle")

        login_value = QLabel(
            self.session.login_time.astimezone().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        login_value.setObjectName("pageSubtitle")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Optional email address")
        self.email_input.setText(self.session.email or "")

        form.addRow("Username", username_value)
        form.addRow("Role", role_value)
        form.addRow("Signed in", login_value)
        form.addRow("Email", self.email_input)

        save_button = QPushButton("Save Email")
        save_button.setObjectName("accentButton")
        save_button.clicked.connect(self._save_email)

        logout_button = QPushButton("Sign Out")
        logout_button.setObjectName("secondaryButton")
        logout_button.clicked.connect(self.logout_requested.emit)

        button_row = QHBoxLayout()
        button_row.addWidget(save_button)
        button_row.addWidget(logout_button)
        button_row.addStretch()

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(form)
        layout.addStretch()
        layout.addLayout(button_row)

        return card

    def _create_password_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")
        card.setMinimumHeight(380)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Change password")
        title.setObjectName("sectionTitle")

        description = QLabel(
            "Use at least 10 characters with uppercase and lowercase "
            "letters, a number, and a special character."
        )
        description.setObjectName("sectionSubtitle")
        description.setWordWrap(True)
        description.setMinimumHeight(58)

        form = QFormLayout()
        form.setSpacing(12)

        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        form.addRow("Current password", self.current_password_input)
        form.addRow("New password", self.new_password_input)
        form.addRow("Confirm password", self.confirm_password_input)

        change_button = QPushButton("Change Password")
        change_button.setObjectName("accentButton")
        change_button.clicked.connect(self._change_password)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(form)
        layout.addStretch()
        layout.addWidget(
            change_button,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )

        return card

    def _save_email(self) -> None:
        try:
            self.session = (
                self.authentication_service.update_own_email(
                    session=self.session,
                    email=self.email_input.text().strip() or None,
                )
            )
        except XtremeCyberError as exc:
            QMessageBox.warning(
                self,
                "Could Not Update Email",
                str(exc),
            )
            return

        QMessageBox.information(
            self,
            "Email Updated",
            "Your email address was updated successfully.",
        )

    def _change_password(self) -> None:
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirmation = self.confirm_password_input.text()

        if not current_password or not new_password:
            QMessageBox.information(
                self,
                "Missing Password",
                "Enter your current password and a new password.",
            )
            return

        if new_password != confirmation:
            QMessageBox.warning(
                self,
                "Passwords Do Not Match",
                "The new password and confirmation do not match.",
            )
            return

        try:
            self.authentication_service.change_own_password(
                session=self.session,
                current_password=current_password,
                new_password=new_password,
            )
        except XtremeCyberError as exc:
            QMessageBox.warning(
                self,
                "Could Not Change Password",
                str(exc),
            )
            return

        self.current_password_input.clear()
        self.new_password_input.clear()
        self.confirm_password_input.clear()

        QMessageBox.information(
            self,
            "Password Changed",
            "Your password was changed successfully. "
            "Use the new password the next time you sign in.",
        )
