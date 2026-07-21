
"""
XtremeCyber splash screen

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
    def __init__(self) -> None:
        super().__init__()

        self.setFixedSize(760, 430)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)

        container = QFrame()
        container.setObjectName("splashContainer")
        container.setStyleSheet(
            """
            QFrame#splashContainer {
                background-color: #08100C;
                border: 1px solid #1C4A31;
                border-radius: 28px;
            }
            QFrame#visualPanel {
                background-color: #0A2417;
                border: 1px solid #13653A;
                border-radius: 22px;
            }
            QFrame#messagePanel {
                background-color: rgba(5, 36, 23, 0.85);
                border: 1px solid #13653A;
                border-radius: 18px;
            }
            QLabel {
                background-color: transparent;
            }
            QLabel#taglineTitle {
                color: #F4FFF8;
                font-size: 17px;
                font-weight: 800;
            }
            QLabel#taglineSubtitle {
                color: #8EB09D;
                font-size: 11px;
            }
            QProgressBar {
                background-color: #122019;
                color: #DFFFF0;
                border: none;
                border-radius: 9px;
                min-height: 18px;
                text-align: center;
                font-weight: 700;
            }
            QProgressBar::chunk {
                background-color: #00E676;
                border-radius: 9px;
            }
            """
        )

        layout = QHBoxLayout(container)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(26)

        # Left visual panel
        visual = QFrame()
        visual.setObjectName("visualPanel")
        visual.setFixedWidth(250)

        visual_layout = QVBoxLayout(visual)
        visual_layout.setContentsMargins(24, 24, 24, 24)
        visual_layout.setSpacing(18)

        logo = QLabel("X")
        logo.setFixedSize(118, 118)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        logo.setStyleSheet(
            """
            background-color: #3C40B8;
            color: #FFFFFF;
            border: 1px solid #6870E0;
            border-radius: 59px;
            """
        )

        visual_layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)
        visual_layout.addStretch()

        message_panel = QFrame()
        message_panel.setObjectName("messagePanel")

        message_layout = QVBoxLayout(message_panel)
        message_layout.setContentsMargins(18, 16, 18, 16)
        message_layout.setSpacing(8)

        tagline = QLabel("Scan.\nUnderstand.\nDefend.")
        tagline.setObjectName("taglineTitle")
        tagline.setWordWrap(True)

        tagline_subtitle = QLabel(
            "Structured vulnerability assessment with a clean and secure workspace."
        )
        tagline_subtitle.setObjectName("taglineSubtitle")
        tagline_subtitle.setWordWrap(True)

        message_layout.addWidget(tagline)
        message_layout.addWidget(tagline_subtitle)

        visual_layout.addWidget(message_panel)

        # Right content panel
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 4, 0, 4)
        content_layout.setSpacing(10)

        title = QLabel(APP_NAME)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFFFFF;")

        subtitle = QLabel("Automated Vulnerability Assessment Platform")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            "color: #95AE9F; font-size: 13px;"
        )

        header_space = QLabel("")
        header_space.setFixedHeight(6)

        self.status_label = QLabel("Connecting to database...")
        self.status_label.setStyleSheet(
            "color: #8EA697; font-size: 13px;"
        )

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(35)

        version = QLabel(f"Version {VERSION}")
        version.setStyleSheet(
            "color: #5F7869; font-size: 11px;"
        )

        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addWidget(header_space)
        content_layout.addStretch()
        content_layout.addWidget(self.status_label)
        content_layout.addWidget(self.progress_bar)
        content_layout.addWidget(version)

        layout.addWidget(visual)
        layout.addWidget(content, 1)

        root.addWidget(container)

    def set_progress(self, value: int, message: str) -> None:
        self.progress_bar.setValue(max(0, min(int(value), 100)))
        self.status_label.setText(message)