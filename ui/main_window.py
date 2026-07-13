"""
Main desktop window for XtremeCyber.
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from config import APP_NAME, VERSION, WINDOW_HEIGHT, WINDOW_WIDTH
from core.constants import Theme
from core.database.repository import ScanRepository, SettingsRepository
from core.logger import get_logger


logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main XtremeCyber application window."""

    theme_change_requested = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.scan_repository = ScanRepository()
        self.settings_repository = SettingsRepository()

        self.navigation_buttons: list[QPushButton] = []

        self.setWindowTitle(
            f"{APP_NAME} - Automated Vulnerability Assessment Platform"
        )
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(1050, 700)

        self._build_ui()
        self._connect_signals()
        self.show_page(0)
        self.refresh_dashboard()

        self.statusBar().showMessage(
            f"{APP_NAME} {VERSION} ready",
            5000,
        )

    def _build_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._create_sidebar())

        main_area = QFrame()
        main_area.setObjectName("contentFrame")

        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._create_top_bar())

        self.page_stack = QStackedWidget()
        self.page_stack.addWidget(self._create_dashboard_page())
        self.page_stack.addWidget(
            self._create_placeholder_page(
                title="Scan",
                subtitle="Configure and launch authorized security scans.",
                message=(
                    "The complete scanning form and scanning engine will be "
                    "implemented in the scanning phase."
                ),
            )
        )
        self.page_stack.addWidget(
            self._create_placeholder_page(
                title="Results",
                subtitle="Review hosts, ports, services, and vulnerabilities.",
                message=(
                    "Detailed result filtering and vulnerability tables will "
                    "be added in a later phase."
                ),
            )
        )
        self.page_stack.addWidget(
            self._create_placeholder_page(
                title="Reports",
                subtitle="Generate and manage assessment reports.",
                message=(
                    "PDF, CSV, and JSON report generation will be added in "
                    "the reporting phase."
                ),
            )
        )
        self.page_stack.addWidget(self._create_settings_page())

        main_layout.addWidget(self.page_stack, 1)

        root_layout.addWidget(main_area, 1)

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(235)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 22, 16, 18)
        layout.setSpacing(8)

        title_label = QLabel(APP_NAME)
        title_label.setObjectName("applicationTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Security Assessment")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setObjectName("pageSubtitle")

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(28)

        navigation_items = [
            ("Dashboard", 0),
            ("Scan", 1),
            ("Results", 2),
            ("Reports", 3),
            ("Settings", 4),
        ]

        for text, page_index in navigation_items:
            button = QPushButton(text)
            button.setObjectName("navigationButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                self._create_navigation_handler(page_index)
            )

            self.navigation_buttons.append(button)
            layout.addWidget(button)

        layout.addStretch()

        version_label = QLabel(f"Version {VERSION}")
        version_label.setObjectName("pageSubtitle")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        authorization_label = QLabel(
            "Authorized use only"
        )
        authorization_label.setObjectName("pageSubtitle")
        authorization_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        authorization_label.setWordWrap(True)

        layout.addWidget(authorization_label)
        layout.addWidget(version_label)

        return sidebar

    def _create_top_bar(self) -> QFrame:
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(76)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(28, 12, 28, 12)

        title_container = QVBoxLayout()
        title_container.setSpacing(1)

        self.top_page_title = QLabel("Dashboard")
        self.top_page_title.setObjectName("sectionTitle")

        self.top_page_subtitle = QLabel(
            "Security assessment overview"
        )
        self.top_page_subtitle.setObjectName("pageSubtitle")

        title_container.addWidget(self.top_page_title)
        title_container.addWidget(self.top_page_subtitle)

        layout.addLayout(title_container)
        layout.addStretch()

        self.theme_button = QPushButton("Switch Theme")
        self.theme_button.setCursor(Qt.CursorShape.PointingHandCursor)

        refresh_button = QPushButton("Refresh")
        refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_button.clicked.connect(self.refresh_dashboard)

        layout.addWidget(refresh_button)
        layout.addWidget(self.theme_button)

        return top_bar

    def _create_dashboard_page(self) -> QWidget:
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        heading = QLabel("Dashboard")
        heading.setObjectName("pageTitle")

        subtitle = QLabel(
            "Overview of XtremeCyber scanning activity and system status."
        )
        subtitle.setObjectName("pageSubtitle")

        layout.addWidget(heading)
        layout.addWidget(subtitle)

        card_grid = QGridLayout()
        card_grid.setHorizontalSpacing(16)
        card_grid.setVerticalSpacing(16)

        self.total_scans_value = QLabel("0")
        self.pending_scans_value = QLabel("0")
        self.completed_scans_value = QLabel("0")
        self.database_status_value = QLabel("Connected")

        cards = [
            (
                "Total Scans",
                self.total_scans_value,
                "All vulnerability assessments",
            ),
            (
                "Pending Scans",
                self.pending_scans_value,
                "Assessments waiting to run",
            ),
            (
                "Completed Scans",
                self.completed_scans_value,
                "Successfully completed scans",
            ),
            (
                "Database",
                self.database_status_value,
                "SQLite storage status",
            ),
        ]

        for index, card_data in enumerate(cards):
            row = index // 4
            column = index % 4
            card_grid.addWidget(
                self._create_stat_card(*card_data),
                row,
                column,
            )

        for column in range(4):
            card_grid.setColumnStretch(column, 1)

        layout.addLayout(card_grid)

        recent_panel = QFrame()
        recent_panel.setObjectName("panelCard")

        recent_layout = QVBoxLayout(recent_panel)
        recent_layout.setContentsMargins(20, 18, 20, 20)
        recent_layout.setSpacing(12)

        recent_header = QHBoxLayout()

        recent_title = QLabel("Recent Scans")
        recent_title.setObjectName("sectionTitle")

        recent_header.addWidget(recent_title)
        recent_header.addStretch()

        start_scan_button = QPushButton("Start New Scan")
        start_scan_button.setObjectName("primaryButton")
        start_scan_button.clicked.connect(lambda: self.show_page(1))

        recent_header.addWidget(start_scan_button)
        recent_layout.addLayout(recent_header)

        self.recent_scans_table = QTableWidget(0, 5)
        self.recent_scans_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Target",
                "Type",
                "Status",
                "Created",
            ]
        )
        self.recent_scans_table.setAlternatingRowColors(True)
        self.recent_scans_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.recent_scans_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.recent_scans_table.verticalHeader().setVisible(False)

        header = self.recent_scans_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        recent_layout.addWidget(self.recent_scans_table)

        layout.addWidget(recent_panel, 1)

        return page

    @staticmethod
    def _create_stat_card(
        title: str,
        value_label: QLabel,
        description: str,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(135)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        value_label.setObjectName("cardValue")

        description_label = QLabel(description)
        description_label.setObjectName("pageSubtitle")
        description_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(description_label)
        layout.addStretch()

        return card

    def _create_placeholder_page(
        self,
        title: str,
        subtitle: str,
        message: str,
    ) -> QWidget:
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("pageSubtitle")

        panel = QFrame()
        panel.setObjectName("panelCard")

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(30, 30, 30, 30)

        placeholder_label = QLabel(message)
        placeholder_label.setObjectName("placeholderText")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setWordWrap(True)

        panel_layout.addStretch()
        panel_layout.addWidget(placeholder_label)
        panel_layout.addStretch()

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(10)
        layout.addWidget(panel, 1)

        return page

    def _create_settings_page(self) -> QWidget:
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(14)

        title_label = QLabel("Settings")
        title_label.setObjectName("pageTitle")

        subtitle_label = QLabel(
            "Manage application appearance and future scan preferences."
        )
        subtitle_label.setObjectName("pageSubtitle")

        panel = QFrame()
        panel.setObjectName("panelCard")
        panel.setMaximumWidth(700)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(24, 24, 24, 24)
        panel_layout.setSpacing(16)

        appearance_title = QLabel("Appearance")
        appearance_title.setObjectName("sectionTitle")

        appearance_description = QLabel(
            "Switch between XtremeCyber dark and light modes."
        )
        appearance_description.setObjectName("pageSubtitle")

        settings_theme_button = QPushButton("Toggle Dark / Light Theme")
        settings_theme_button.setObjectName("primaryButton")
        settings_theme_button.clicked.connect(
            self.theme_change_requested.emit
        )

        panel_layout.addWidget(appearance_title)
        panel_layout.addWidget(appearance_description)
        panel_layout.addWidget(settings_theme_button)
        panel_layout.addStretch()

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(10)
        layout.addWidget(panel)
        layout.addStretch()

        return page

    def _connect_signals(self) -> None:
        self.theme_button.clicked.connect(
            self.theme_change_requested.emit
        )

    def _create_navigation_handler(
        self,
        page_index: int,
    ) -> Callable[[], None]:
        return lambda: self.show_page(page_index)

    def show_page(self, page_index: int) -> None:
        """Display a page and update navigation state."""

        if page_index < 0 or page_index >= self.page_stack.count():
            return

        self.page_stack.setCurrentIndex(page_index)

        titles = [
            ("Dashboard", "Security assessment overview"),
            ("Scan", "Configure and launch an assessment"),
            ("Results", "Review discovered security information"),
            ("Reports", "Generate and manage security reports"),
            ("Settings", "Configure XtremeCyber preferences"),
        ]

        title, subtitle = titles[page_index]
        self.top_page_title.setText(title)
        self.top_page_subtitle.setText(subtitle)

        for index, button in enumerate(self.navigation_buttons):
            button.setChecked(index == page_index)

        if page_index == 0:
            self.refresh_dashboard()

    def refresh_dashboard(self) -> None:
        """Refresh dashboard statistics and recent scan records."""

        try:
            all_scans = self.scan_repository.get_recent(limit=100)

            total_scans = len(all_scans)
            pending_scans = sum(
                1
                for scan in all_scans
                if scan.get("status") == "pending"
            )
            completed_scans = sum(
                1
                for scan in all_scans
                if scan.get("status") == "completed"
            )

            self.total_scans_value.setText(str(total_scans))
            self.pending_scans_value.setText(str(pending_scans))
            self.completed_scans_value.setText(str(completed_scans))
            self.database_status_value.setText("Connected")

            recent_scans = self.scan_repository.get_recent(limit=10)
            self._populate_recent_scans(recent_scans)

            self.statusBar().showMessage(
                "Dashboard refreshed successfully.",
                3000,
            )

        except Exception as exc:
            logger.exception("Could not refresh dashboard.")
            self.database_status_value.setText("Error")
            self.statusBar().showMessage(
                f"Dashboard refresh failed: {exc}",
                5000,
            )

    def _populate_recent_scans(
        self,
        scans: list[dict],
    ) -> None:
        self.recent_scans_table.setRowCount(len(scans))

        for row_index, scan in enumerate(scans):
            values = [
                str(scan.get("id", "")),
                str(scan.get("target", "")),
                str(scan.get("scan_type", "")).title(),
                str(scan.get("status", "")).title(),
                str(scan.get("created_at", "")),
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)

                if column_index == 0:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.recent_scans_table.setItem(
                    row_index,
                    column_index,
                    item,
                )

    def set_active_theme(self, theme: Theme) -> None:
        """Update theme button text after applying a theme."""

        if theme == Theme.DARK:
            self.theme_button.setText("Use Light Theme")
        else:
            self.theme_button.setText("Use Dark Theme")