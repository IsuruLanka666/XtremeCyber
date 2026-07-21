"""
Administrator user-management interface for XtremeCyber.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.auth.service import AuthenticationService
from core.auth.session import UserSession
from core.exceptions import XtremeCyberError


class CleanTableDelegate(QStyledItemDelegate):
    """Remove the native focus rectangle from table cells."""

    def paint(self, painter, option, index) -> None:
        clean_option = QStyleOptionViewItem(option)

        clean_option.state &= ~QStyle.StateFlag.State_HasFocus

        super().paint(
            painter,
            clean_option,
            index,
        )


class CreateUserDialog(QDialog):
    """Dialog used by administrators to create accounts."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Create XtremeCyber User")
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Create user account")
        title.setObjectName("sectionTitle")

        description = QLabel(
            "Create an administrator, analyst, or viewer account."
        )
        description.setObjectName("sectionSubtitle")
        description.setWordWrap(True)

        form = QFormLayout()
        form.setSpacing(12)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g. analyst01")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Optional email address")

        self.role_input = QComboBox()
        self.role_input.addItems(["viewer", "analyst", "admin"])

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText(
            "10+ characters with uppercase, number, and symbol"
        )

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.confirm_password_input.setPlaceholderText(
            "Re-enter the password"
        )

        form.addRow("Username", self.username_input)
        form.addRow("Email", self.email_input)
        form.addRow("Role", self.role_input)
        form.addRow("Password", self.password_input)
        form.addRow("Confirm password", self.confirm_password_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #FF8FAE;")
        self.error_label.setWordWrap(True)
        self.error_label.setMinimumHeight(36)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
        )
        buttons.button(
            QDialogButtonBox.StandardButton.Ok
        ).setText("Create User")
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(form)
        layout.addWidget(self.error_label)
        layout.addWidget(buttons)

    def _validate_and_accept(self) -> None:
        if not self.username_input.text().strip():
            self.error_label.setText("Username is required.")
            return

        if not self.password_input.text():
            self.error_label.setText("Password is required.")
            return

        if (
            self.password_input.text()
            != self.confirm_password_input.text()
        ):
            self.error_label.setText("Passwords do not match.")
            return

        self.accept()

    def values(self) -> dict[str, str | None]:
        return {
            "username": self.username_input.text().strip(),
            "email": self.email_input.text().strip() or None,
            "role": self.role_input.currentText(),
            "password": self.password_input.text(),
        }


class ResetPasswordDialog(QDialog):
    """Dialog for an administrator password reset."""

    def __init__(
        self,
        username: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle("Reset Password")
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel(f"Reset password for {username}")
        title.setObjectName("sectionTitle")

        description = QLabel(
            "The new password must meet the XtremeCyber password policy."
        )
        description.setObjectName("sectionSubtitle")
        description.setWordWrap(True)

        form = QFormLayout()
        form.setSpacing(12)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("New password", self.password_input)
        form.addRow("Confirm password", self.confirm_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #FF8FAE;")
        self.error_label.setWordWrap(True)
        self.error_label.setMinimumHeight(36)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
        )
        buttons.button(
            QDialogButtonBox.StandardButton.Ok
        ).setText("Reset Password")
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(form)
        layout.addWidget(self.error_label)
        layout.addWidget(buttons)

    def _validate_and_accept(self) -> None:
        if not self.password_input.text():
            self.error_label.setText("Enter a new password.")
            return

        if self.password_input.text() != self.confirm_input.text():
            self.error_label.setText("Passwords do not match.")
            return

        self.accept()

    def password(self) -> str:
        return self.password_input.text()


class UserManagementPage(QWidget):
    """Administrator-only account-management page."""

    def __init__(
        self,
        session: UserSession,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.session = session
        self.authentication_service = AuthenticationService()
        self.users: list[dict] = []

        self.setObjectName("pageBackground")

        self._build_ui()
        self.refresh_users()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 34)
        layout.setSpacing(18)

        header = QHBoxLayout()

        header_text = QVBoxLayout()
        header_text.setSpacing(3)

        title = QLabel("User management")
        title.setObjectName("accentHeading")
        title.setMinimumHeight(52)

        subtitle = QLabel(
            "Create accounts, assign roles, control access, "
            "and reset user passwords."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        subtitle.setMinimumHeight(40)

        header_text.addWidget(title)
        header_text.addWidget(subtitle)

        create_button = QPushButton("Create User")
        create_button.setObjectName("accentButton")
        create_button.clicked.connect(self._create_user)

        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName("secondaryButton")
        refresh_button.clicked.connect(self.refresh_users)

        header.addLayout(header_text)
        header.addStretch()
        header.addWidget(refresh_button)
        header.addWidget(create_button)

        layout.addLayout(header)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(14)

        self.total_users_card = self._create_summary_card(
            "Total users",
            "0",
        )
        self.active_users_card = self._create_summary_card(
            "Active users",
            "0",
        )
        self.admin_users_card = self._create_summary_card(
            "Administrators",
            "0",
        )

        summary_row.addWidget(self.total_users_card)
        summary_row.addWidget(self.active_users_card)
        summary_row.addWidget(self.admin_users_card)

        layout.addLayout(summary_row)

        table_card = QFrame()
        table_card.setObjectName("contentCard")

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(14)

        table_title = QLabel("Accounts")
        table_title.setObjectName("sectionTitle")

        table_subtitle = QLabel(
            "Select a user to change role, access status, or password."
        )
        table_subtitle.setObjectName("sectionSubtitle")

        table_layout.addWidget(table_title)
        table_layout.addWidget(table_subtitle)

        self.user_table = QTableWidget(0, 7)
        self.user_table.setHorizontalHeaderLabels(
            [
                "ID",
                "USERNAME",
                "EMAIL",
                "ROLE",
                "STATUS",
                "LAST LOGIN",
                "CREATED",
            ]
        )
        self.user_table.setAlternatingRowColors(True)
        self.user_table.setShowGrid(False)
        self.user_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.user_table.setStyleSheet(
            """
            QTableWidget {
                outline: none;
            }

            QTableWidget::item {
                border: none;
                padding: 8px;
            }

            QTableWidget::item:focus {
                border: none;
                outline: none;
            }
            """
        )
        self.user_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.user_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.user_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.user_table.verticalHeader().setVisible(False)

        self.user_table.setItemDelegate(
            CleanTableDelegate(self.user_table)
        )

        self.user_table.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        self.user_table.setShowGrid(False)

        self.user_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.user_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        table_header = self.user_table.horizontalHeader()
        table_header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        table_header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        table_header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch,
        )

        for column in (3, 4, 5, 6):
            table_header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )

        table_layout.addWidget(self.user_table)

        actions = QHBoxLayout()
        actions.setSpacing(10)

        role_button = QPushButton("Change Role")
        role_button.setObjectName("secondaryButton")
        role_button.clicked.connect(self._change_role)

        status_button = QPushButton("Enable / Disable")
        status_button.setObjectName("secondaryButton")
        status_button.clicked.connect(self._toggle_status)

        password_button = QPushButton("Reset Password")
        password_button.setObjectName("secondaryButton")
        password_button.clicked.connect(self._reset_password)

        actions.addWidget(role_button)
        actions.addWidget(status_button)
        actions.addWidget(password_button)
        actions.addStretch()

        table_layout.addLayout(actions)
        layout.addWidget(table_card, 1)

    @staticmethod
    def _create_summary_card(
        title: str,
        value: str,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(112)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        value_label = QLabel(value)
        value_label.setObjectName("cardValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.value_label = value_label
        return card

    def refresh_users(self) -> None:
        try:
            self.users = (
                self.authentication_service.list_users_as_admin(
                    self.session
                )
            )
        except XtremeCyberError as exc:
            QMessageBox.critical(
                self,
                "User Management Error",
                str(exc),
            )
            return

        self._populate_table()
        self._update_summary()

    def _populate_table(self) -> None:
        self.user_table.setRowCount(len(self.users))

        for row_index, user in enumerate(self.users):
            values = [
                str(user["id"]),
                str(user["username"]),
                str(user["email"] or ""),
                str(user["role"]).title(),
                "Active" if bool(user["is_active"]) else "Disabled",
                self._format_time(user["last_login_at"]),
                self._format_time(user["created_at"]),
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)

                if column_index in (0, 3, 4):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.user_table.setItem(
                    row_index,
                    column_index,
                    item,
                )

    def _update_summary(self) -> None:
        total = len(self.users)
        active = sum(
            1 for user in self.users if bool(user["is_active"])
        )
        admins = sum(
            1
            for user in self.users
            if str(user["role"]) == "admin"
        )

        self.total_users_card.value_label.setText(str(total))
        self.active_users_card.value_label.setText(str(active))
        self.admin_users_card.value_label.setText(str(admins))

    def _selected_user(self) -> dict | None:
        row = self.user_table.currentRow()

        if row < 0 or row >= len(self.users):
            QMessageBox.information(
                self,
                "Select User",
                "Select a user account first.",
            )
            return None

        return self.users[row]

    def _create_user(self) -> None:
        dialog = CreateUserDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        values = dialog.values()

        try:
            self.authentication_service.create_user_as_admin(
                session=self.session,
                username=str(values["username"]),
                password=str(values["password"]),
                email=(
                    str(values["email"])
                    if values["email"]
                    else None
                ),
                role=str(values["role"]),
            )
        except XtremeCyberError as exc:
            QMessageBox.warning(
                self,
                "Could Not Create User",
                str(exc),
            )
            return

        QMessageBox.information(
            self,
            "User Created",
            "The user account was created successfully.",
        )
        self.refresh_users()

    def _change_role(self) -> None:
        user = self._selected_user()

        if user is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Change User Role")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel(
            f"Change role for {user['username']}"
        )
        title.setObjectName("sectionTitle")

        role_input = QComboBox()
        role_input.addItems(["viewer", "analyst", "admin"])
        role_input.setCurrentText(str(user["role"]))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(title)
        layout.addWidget(role_input)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            self.authentication_service.update_user_role_as_admin(
                session=self.session,
                user_id=int(user["id"]),
                role=role_input.currentText(),
            )
        except XtremeCyberError as exc:
            QMessageBox.warning(
                self,
                "Could Not Change Role",
                str(exc),
            )
            return

        self.refresh_users()

    def _toggle_status(self) -> None:
        user = self._selected_user()

        if user is None:
            return

        currently_active = bool(user["is_active"])
        action = "disable" if currently_active else "enable"

        answer = QMessageBox.question(
            self,
            "Confirm Account Status",
            (
                f"Do you want to {action} the account "
                f"'{user['username']}'?"
            ),
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.authentication_service.set_user_active_as_admin(
                session=self.session,
                user_id=int(user["id"]),
                is_active=not currently_active,
            )
        except XtremeCyberError as exc:
            QMessageBox.warning(
                self,
                "Could Not Update Account",
                str(exc),
            )
            return

        self.refresh_users()

    def _reset_password(self) -> None:
        user = self._selected_user()

        if user is None:
            return

        dialog = ResetPasswordDialog(
            username=str(user["username"]),
            parent=self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            self.authentication_service.reset_user_password_as_admin(
                session=self.session,
                user_id=int(user["id"]),
                new_password=dialog.password(),
            )
        except XtremeCyberError as exc:
            QMessageBox.warning(
                self,
                "Could Not Reset Password",
                str(exc),
            )
            return

        QMessageBox.information(
            self,
            "Password Reset",
            "The password was reset successfully.",
        )

    @staticmethod
    def _format_time(value: object) -> str:
        if not value:
            return "Never"

        formatted = str(value).replace("T", " ")

        if "+" in formatted:
            formatted = formatted.split("+", maxsplit=1)[0]

        return formatted
