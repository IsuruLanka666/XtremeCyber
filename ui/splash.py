"""
Splash screen for XtremeCyber.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from config import APP_NAME, VERSION


class SplashScreen(QWidget):
    """Rounded frameless splash screen used during startup."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} Startup")
        self.setFixedSize(680, 390)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._build_ui()

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)

        container = QFrame()
        container.setObjectName("splashContainer")
        container.setStyleSheet(
            """
            QFrame#splashContainer {
                background-color: #101632;
                border: 1px solid #2D3760;
                border-radius: 28px;
            }
            QFrame#splashVisualPanel {
                background-color: #5265FF;
                border: none;
                border-radius: 22px;
            }
            QLabel { background-color: transparent; }
            QProgressBar {
                background-color: #20294B;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                min-height: 17px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #5265FF;
                border-radius: 8px;
            }
            """
        )

        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.setSpacing(28)

        visual_panel = QFrame()
        visual_panel.setObjectName("splashVisualPanel")
        visual_panel.setFixedWidth(235)

        visual_layout = QVBoxLayout(visual_panel)
        visual_layout.setContentsMargins(28, 30, 28, 30)

        shield_label = QLabel("XC")
        shield_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shield_label.setFixedSize(92, 92)
        shield_label.setFont(QFont("Segoe UI", 29, QFont.Weight.Bold))
        shield_label.setStyleSheet(
            """
            QLabel {
                background-color: #FFFFFF;
                color: #5265FF;
                border-radius: 46px;
            }
            """
        )

        visual_layout.addWidget(
            shield_label,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        visual_layout.addStretch()

        visual_title = QLabel("Discover.\nAssess.\nProtect.")
        visual_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        visual_title.setStyleSheet("color: #FFFFFF;")

        visual_description = QLabel(
            "A modern vulnerability assessment workspace."
        )
        visual_description.setWordWrap(True)
        visual_description.setStyleSheet(
            "color: #E1E5FF; font-size: 12px;"
        )

        visual_layout.addWidget(visual_title)
        visual_layout.addSpacing(8)
        visual_layout.addWidget(visual_description)

        content_panel = QWidget()
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(8, 25, 12, 20)
        content_layout.setSpacing(10)

        product_label = QLabel("SECURITY PLATFORM")
        product_label.setStyleSheet(
            "color: #7F8BC0; font-size: 10px; font-weight: 700;"
        )

        title_label = QLabel(APP_NAME)
        title_label.setFont(QFont("Segoe UI", 29, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FFFFFF;")

        subtitle_label = QLabel(
            "Automated Vulnerability Assessment Platform"
        )
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet(
            "color: #A6AFD0; font-size: 13px;"
        )

        content_layout.addWidget(product_label)
        content_layout.addWidget(title_label)
        content_layout.addWidget(subtitle_label)
        content_layout.addStretch()

        self.status_label = QLabel("Preparing secure workspace...")
        self.status_label.setStyleSheet(
            "color: #98A2C7; font-size: 12px;"
        )

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        version_label = QLabel(f"Version {VERSION}")
        version_label.setStyleSheet(
            "color: #646F99; font-size: 10px;"
        )

        content_layout.addWidget(self.status_label)
        content_layout.addWidget(self.progress_bar)
        content_layout.addWidget(version_label)

        container_layout.addWidget(visual_panel)
        container_layout.addWidget(content_panel, 1)
        root_layout.addWidget(container)

    def set_progress(self, value: int, message: str) -> None:
        self.progress_bar.setValue(max(0, min(int(value), 100)))
        self.status_label.setText(message)
