"""
Splash screen displayed while XtremeCyber starts.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from config import APP_NAME, VERSION


class SplashScreen(QWidget):
    """Custom frameless startup splash screen."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} Startup")
        self.setFixedSize(560, 330)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._build_ui()

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        container = QFrame()
        container.setObjectName("splashContainer")
        container.setStyleSheet(
            """
            QFrame#splashContainer {
                background-color: #0F172A;
                border: 1px solid #22D3EE;
                border-radius: 18px;
            }
            """
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(45, 40, 45, 35)
        layout.setSpacing(18)

        logo_label = QLabel("XC")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFixedSize(82, 82)
        logo_label.setFont(QFont("Segoe UI", 27, QFont.Weight.Bold))
        logo_label.setStyleSheet(
            """
            QLabel {
                background-color: #0891B2;
                color: white;
                border-radius: 41px;
            }
            """
        )

        logo_row = QVBoxLayout()
        logo_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_row.addWidget(logo_label)

        title_label = QLabel(APP_NAME)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #67E8F9;")

        subtitle_label = QLabel(
            "Automated Vulnerability Assessment Platform"
        )
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(
            "color: #CBD5E1; font-size: 14px;"
        )

        self.status_label = QLabel("Preparing application...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #94A3B8; font-size: 12px;"
        )

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        version_label = QLabel(f"Version {VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet(
            "color: #64748B; font-size: 11px;"
        )

        layout.addLayout(logo_row)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(version_label)

        outer_layout.addWidget(container)

    def set_progress(self, value: int, message: str) -> None:
        """Update progress and startup message."""

        safe_value = max(0, min(int(value), 100))
        self.progress_bar.setValue(safe_value)
        self.status_label.setText(message)