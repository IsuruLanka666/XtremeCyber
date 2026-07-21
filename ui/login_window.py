"""
XtremeCyber login window.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import APP_NAME, VERSION
from core.auth.service import AuthenticationService
from core.exceptions import AuthenticationError


class LoginWindow(QWidget):
    """Dark neon-green login screen."""

    login_succeeded = Signal(object)

    def __init__(self) -> None:
        super().__init__()

        self.authentication_service = AuthenticationService()

        self.setWindowTitle(f"{APP_NAME} Login")
        self.setMinimumSize(980, 650)
        self.resize(1120, 720)

        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(
            """
            QWidget#loginRoot {
                background-color: #070B0D;
            }

            QFrame#visualPanel {
                background-color: #0A2417;
                border: 1px solid #13653A;
                border-radius: 28px;
            }

            QFrame#loginCard {
                background-color: #0C1215;
                border: 1px solid #1A2822;
                border-radius: 24px;
            }

            QLabel {
                background-color: transparent;
                color: #FFFFFF;
                font-family: "Segoe UI";
            }

            QLabel#mutedText {
                color: #82968A;
                font-size: 13px;
            }

            QLabel#errorText {
                color: #FF8FAE;
                font-size: 12px;
            }

            QLineEdit {
                background-color: #0A1012;
                color: #FFFFFF;
                border: 1px solid #22342B;
                border-radius: 12px;
                padding: 12px 14px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 1px solid #00E676;
            }

            QPushButton#loginButton {
                background-color: #00D96B;
                color: #06110A;
                border: none;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                font-weight: 800;
            }

            QPushButton#loginButton:hover {
                background-color: #36F58D;
            }

            QCheckBox {
                color: #A8C6B5;
                spacing: 8px;
            }
            """
        )

        root = QWidget()
        root.setObjectName("loginRoot")

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(34, 34, 34, 34)
        root_layout.setSpacing(28)

        visual_panel = QFrame()
        visual_panel.setObjectName("visualPanel")
        visual_panel.setMinimumWidth(430)

        visual_layout = QVBoxLayout(visual_panel)
        visual_layout.setContentsMargins(42, 42, 42, 42)

        logo = QLabel("X")
        logo.setFixedSize(98, 98)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFont(QFont("Segoe UI", 31, QFont.Weight.Bold))
        logo.setStyleSheet(
            """
            background-color: #353AA6;
            color: #FFFFFF;
            border: 1px solid #545ACC;
            border-radius: 49px;
            """
        )

        visual_title = QLabel(
            "Secure visibility.\nClear findings.\nStronger defenses."
        )
        visual_title.setFont(
            QFont("Segoe UI", 28, QFont.Weight.Bold)
        )

        visual_description = QLabel(
            "XtremeCyber brings authorized vulnerability assessment, "
            "result organization, and reporting into one focused workspace."
        )
        visual_description.setWordWrap(True)
        visual_description.setStyleSheet(
            "color: #96AD9F; font-size: 14px;"
        )

        visual_layout.addWidget(logo)
        visual_layout.addStretch()
        visual_layout.addWidget(visual_title)
        visual_layout.addSpacing(14)
        visual_layout.addWidget(visual_description)

        login_card = QFrame()
        login_card.setObjectName("loginCard")
        login_card.setMaximumWidth(470)

        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(42, 42, 42, 42)
        card_layout.setSpacing(13)

        product_label = QLabel("XTREMECYBER ACCESS")
        product_label.setStyleSheet(
            "color: #3CF28A; font-size: 10px; font-weight: 800;"
        )

        heading = QLabel("Welcome back")
        heading.setFont(QFont("Segoe UI", 27, QFont.Weight.Bold))

        description = QLabel(
            "Sign in to continue to your security assessment workspace."
        )
        description.setObjectName("mutedText")
        description.setWordWrap(True)

        username_label = QLabel("Username")
        username_label.setStyleSheet("font-weight: 650;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setClearButtonEnabled(True)

        password_label = QLabel("Password")
        password_label.setStyleSheet("font-weight: 650;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        show_password = QCheckBox("Show password")
        show_password.toggled.connect(self._toggle_password_visibility)

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorText")
        self.error_label.setWordWrap(True)
        self.error_label.setMinimumHeight(34)

        self.login_button = QPushButton("Sign In")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self._attempt_login)

        self.password_input.returnPressed.connect(self._attempt_login)
        self.username_input.returnPressed.connect(
            self.password_input.setFocus
        )

        version_label = QLabel(f"Version {VERSION}")
        version_label.setObjectName("mutedText")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(product_label)
        card_layout.addWidget(heading)
        card_layout.addWidget(description)
        card_layout.addSpacing(14)
        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(show_password)
        card_layout.addWidget(self.error_label)
        card_layout.addWidget(self.login_button)
        card_layout.addStretch()
        card_layout.addWidget(version_label)

        root_layout.addWidget(visual_panel, 1)
        root_layout.addWidget(
            login_card,
            1,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(root)

        self.username_input.setFocus()

    def _toggle_password_visibility(self, visible: bool) -> None:
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Normal
            if visible
            else QLineEdit.EchoMode.Password
        )

    def _attempt_login(self) -> None:
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.error_label.setText(
                "Enter both your username and password."
            )
            return

        self.login_button.setEnabled(False)
        self.error_label.clear()

        try:
            session = self.authentication_service.authenticate(
                username,
                password,
            )
        except AuthenticationError as exc:
            self.error_label.setText(str(exc))
            self.password_input.clear()
            self.password_input.setFocus()
        except Exception:
            self.error_label.setText(
                "Login could not be completed. Check the application log."
            )
        else:
            self.login_succeeded.emit(session)
        finally:
            self.login_button.setEnabled(True)
