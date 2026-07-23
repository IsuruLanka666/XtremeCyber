
"""
XtremeCyber main window.

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from core.auth.permissions import Permission
from core.auth.permissions import Permission
from ui.account_page import AccountPage
from ui.user_management_page import UserManagementPage

from core.scanning.persistence import ScanRunRepository

from ui.results_page import ResultsPage

from ui.scan_page import ScanPage

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
    QScrollArea,
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

if TYPE_CHECKING:
    from core.auth.session import UserSession


logger = get_logger(__name__)


class MainWindow(QMainWindow):
    theme_change_requested = Signal()
    logout_requested = Signal()

    def __init__(self, session: Optional[UserSession] = None) -> None:
        super().__init__()

        self.session = session
        self.scan_repository = ScanRepository()
        self.scan_history_repository = ScanRunRepository()
        self.scan_repository = self.scan_history_repository
        self.settings_repository = SettingsRepository()
        self.navigation_buttons: list[QPushButton] = []

        self.setWindowTitle(
            f"{APP_NAME} - Automated Vulnerability Assessment Platform"
        )
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(1160, 740)

        self._build_ui()
        self._connect_signals()
        self.show_page(0)
        self.refresh_dashboard()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("applicationRoot")
        self.setCentralWidget(root)

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._create_sidebar())

        main_area = QFrame()
        main_area.setObjectName("mainArea")

        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._create_top_bar())

        self.page_stack = QStackedWidget()
        self.page_stack.addWidget(self._create_dashboard_page())
        self.scan_page = ScanPage(
            session=self.session
        )

        self.scan_page.configuration_ready.connect(
            self._handle_scan_configuration
        )

        self.scan_page.scan_completed.connect(
            self._handle_scan_completed
        )

        self.scan_page.scan_saved.connect(
            self._handle_scan_saved
        )

        self.scan_page.analysis_completed.connect(
            self._handle_analysis_completed
        )

        self.page_stack.addWidget(self.scan_page)
        self.results_page = ResultsPage(
            session=self.session
        )
        self.page_stack.addWidget(
            self.results_page
        )

        
        self.page_stack.addWidget(
            self._create_placeholder_page(
                "Security reports",
                "Create clear reports for completed assessments.",
                "Professional report centre",
                (
                    "PDF, CSV, and JSON exports, report previews, saved "
                    "reports, and download management will be implemented "
                    "during the reporting phase."
                ),
                "View Reports",
            )
        )
        self.page_stack.addWidget(self._create_settings_page())
        
        if (
            self.session is not None
            and self.session.can(Permission.MANAGE_USERS)
        ):
            self.page_stack.addWidget(
                UserManagementPage(
                    session=self.session
                )
            )
      
        else:
            self.page_stack.addWidget(
                QWidget()
        )

        self.account_page = AccountPage(
            session=self.session
        )

        self.account_page.logout_requested.connect(
            self.logout_requested.emit
        )

        self.page_stack.addWidget(
            self.account_page
        )

        main_layout.addWidget(self.page_stack, 1)
        root_layout.addWidget(main_area, 1)

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(284)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 14, 16, 18)
        layout.setSpacing(10)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)

        icon = QFrame()
        icon.setObjectName("brandIcon")
        icon.setFixedSize(52, 52)

        icon_layout = QVBoxLayout(icon)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        initials = QLabel("X")
        initials.setObjectName("brandInitials")
        initials.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(initials)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(1)

        title = QLabel(APP_NAME)
        title.setObjectName("applicationTitle")

        subtitle = QLabel("Cybersecurity workspace")
        subtitle.setObjectName("applicationSubtitle")

        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)

        brand_row.addWidget(icon)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()

        layout.addLayout(brand_row)
        layout.addSpacing(26)

        label = QLabel("WORKSPACE")
        label.setObjectName("navigationSectionLabel")
        layout.addWidget(label)

        for text, index in [
            ("Overview", 0),
            ("New Scan", 1),
            ("Results", 2),
            ("Reports", 3),
        ]:
            layout.addWidget(self._create_nav_button(text, index))

        layout.addSpacing(16)

        label = QLabel("APPLICATION")
        label.setObjectName("navigationSectionLabel")
        layout.addWidget(label)
        layout.addWidget(self._create_nav_button("Settings", 4))

        if self.session is not None and self.session.is_admin:
            layout.addWidget(
                self._create_nav_button("Users", 5)
            )
        
        layout.addStretch()

        warning = QFrame()
        warning.setObjectName("compactInfoCard")

        warning_layout = QVBoxLayout(warning)
        warning_layout.setContentsMargins(15, 15, 15, 15)
        warning_layout.setSpacing(6)

        warning_title = QLabel("Authorized use only")
        warning_title.setObjectName("sectionTitle")

        warning_text = QLabel(
            "Assess only systems you own or have explicit permission to test."
        )
        warning_text.setObjectName("sectionSubtitle")
        warning_text.setWordWrap(True)
        warning_text.setMinimumHeight(48)

        version = QLabel(f"XtremeCyber {VERSION}")
        version.setObjectName("applicationSubtitle")

        warning_layout.addWidget(warning_title)
        warning_layout.addWidget(warning_text)
        warning_layout.addWidget(version)

        layout.addWidget(warning)
        return sidebar

    def _create_nav_button(self, text: str, index: int) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("navigationButton")
        button.setCheckable(True)
        button.clicked.connect(self._create_navigation_handler(index))
        self.navigation_buttons.append(button)
        return button

    def _create_top_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("topBar")
        bar.setFixedHeight(90)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(34, 12, 34, 12)

        text = QVBoxLayout()
        text.setSpacing(2)

        self.top_page_title = QLabel("Overview")
        self.top_page_title.setObjectName("topPageTitle")
        self.top_page_title.setMinimumHeight(28)

        self.top_page_subtitle = QLabel(
            "Security assessment activity at a glance"
        )
        self.top_page_subtitle.setObjectName("topPageSubtitle")
        self.top_page_subtitle.setMinimumHeight(20)

        text.addWidget(self.top_page_title)
        text.addWidget(self.top_page_subtitle)

        layout.addLayout(text)
        layout.addStretch()

        if self.session is not None:
            user = QLabel(
                f"{self.session.username} • {self.session.role.title()}"
            )
            user.setObjectName("topPageSubtitle")
            layout.addWidget(user)

        refresh = QPushButton("Refresh")
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.refresh_dashboard)

        self.theme_button = QPushButton("Light Mode")
        self.theme_button.setObjectName("accentButton")

        layout.addWidget(refresh)
        layout.addWidget(self.theme_button)

        if self.session is not None:
            logout = QPushButton("Logout")
            logout.setObjectName("secondaryButton")
            logout.clicked.connect(self.logout_requested.emit)
            layout.addWidget(logout)

        return bar

    def _create_dashboard_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("pageBackground")

        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        content.setObjectName("pageBackground")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(34, 28, 34, 34)
        layout.setSpacing(22)

        heading = QLabel("Security overview")
        heading.setObjectName("accentHeading")
        heading.setWordWrap(True)
        heading.setMinimumHeight(52)

        description = QLabel(
            "Monitor assessments, review scan activity, and begin a new "
            "authorized vulnerability evaluation."
        )
        description.setObjectName("pageSubtitle")
        description.setWordWrap(True)
        description.setMinimumHeight(42)

        layout.addWidget(heading)
        layout.addWidget(description)
        layout.addWidget(self._create_hero_panel())

        self.total_scans_value = QLabel("0")
        self.pending_scans_value = QLabel("0")
        self.completed_scans_value = QLabel("0")
        self.database_status_value = QLabel("Connected")

        grid = QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(15)

        data = [
            ("Total assessments", self.total_scans_value, "All stored vulnerability scans", "SC", "statIconBlue"),
            ("Waiting scans", self.pending_scans_value, "Assessments pending execution", "PD", "statIconPurple"),
            ("Completed", self.completed_scans_value, "Successfully completed scans", "OK", "statIconGreen"),
            ("Data storage", self.database_status_value, "Local SQLite storage layer", "DB", "statIconOrange"),
        ]

        for column, card_data in enumerate(data):
            grid.addWidget(self._create_stat_card(*card_data), 0, column)
            grid.setColumnStretch(column, 1)

        layout.addLayout(grid)
        layout.addWidget(self._create_recent_scans_panel(), 1)

        scroll.setWidget(content)
        outer.addWidget(scroll)
        return page

    def _create_hero_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("heroPanel")
        panel.setMinimumHeight(235)

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(32, 29, 32, 29)
        layout.setSpacing(24)

        text = QVBoxLayout()
        text.setSpacing(10)

        badge = QLabel("DEFENSIVE SECURITY ASSESSMENT PLATFORM")
        badge.setObjectName("heroBadge")
        badge.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed,
        )

        title = QLabel("Welcome to XtremeCyber")
        title.setObjectName("heroTitle")
        title.setWordWrap(True)
        title.setMinimumHeight(40)

        highlight = QLabel(
            "Understand your attack surface before someone else does."
        )
        highlight.setObjectName("heroHighlight")
        highlight.setWordWrap(True)
        highlight.setMinimumHeight(72)

        description = QLabel(
            "Launch structured vulnerability assessments, organize findings, "
            "and produce clear defensive reports from one focused workspace."
        )
        description.setObjectName("heroDescription")
        description.setWordWrap(True)
        description.setMinimumHeight(48)

        actions = QHBoxLayout()

        start = QPushButton("Start New Scan")
        start.setObjectName("primaryButton")
        start.clicked.connect(lambda: self.show_page(1))

        results = QPushButton("Review Results")
        results.setObjectName("secondaryButton")
        results.clicked.connect(lambda: self.show_page(2))

        actions.addWidget(start)
        actions.addWidget(results)
        actions.addStretch()

        text.addWidget(badge)
        text.addWidget(title)
        text.addWidget(highlight)
        text.addWidget(description)
        text.addStretch()
        text.addLayout(actions)

        visual = QFrame()
        visual.setObjectName("heroVisual")
        visual.setFixedSize(240, 180)

        visual_layout = QVBoxLayout(visual)

        orb = QFrame()
        orb.setObjectName("heroOrb")
        orb.setFixedSize(104, 104)

        orb_layout = QVBoxLayout(orb)
        orb_layout.setContentsMargins(0, 0, 0, 0)

        orb_text = QLabel("X")
        orb_text.setObjectName("heroOrbText")
        orb_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        orb_layout.addWidget(orb_text)

        visual_layout.addStretch()
        visual_layout.addWidget(orb, alignment=Qt.AlignmentFlag.AlignCenter)
        visual_layout.addStretch()

        layout.addLayout(text, 1)
        layout.addWidget(visual)
        return panel

    @staticmethod
    def _create_stat_card(
        title: str,
        value_label: QLabel,
        description: str,
        icon_text: str,
        icon_name: str,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(165)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 17, 18, 17)
        layout.setSpacing(8)

        icon = QFrame()
        icon.setObjectName(icon_name)
        icon.setFixedSize(44, 44)

        icon_layout = QVBoxLayout(icon)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_text_label = QLabel(icon_text)
        icon_text_label.setObjectName("statIconText")
        icon_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_text_label)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)
        title_label.setMinimumHeight(20)

        value_label.setObjectName("cardValue")
        value_label.setMinimumHeight(38)

        description_label = QLabel(description)
        description_label.setObjectName("cardDescription")
        description_label.setWordWrap(True)
        description_label.setMinimumHeight(34)

        layout.addWidget(icon)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(description_label)
        return card

    def _create_recent_scans_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("contentCard")
        panel.setMinimumHeight(340)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(21, 20, 21, 21)

        header = QHBoxLayout()
        header_text = QVBoxLayout()

        title = QLabel("Recent assessments")
        title.setObjectName("sectionTitle")
        title.setMinimumHeight(26)

        subtitle = QLabel(
            "Latest vulnerability scans stored in your local workspace."
        )
        subtitle.setObjectName("sectionSubtitle")
        subtitle.setMinimumHeight(20)

        header_text.addWidget(title)
        header_text.addWidget(subtitle)

        new_button = QPushButton("New Assessment")
        new_button.setObjectName("accentButton")
        new_button.clicked.connect(lambda: self.show_page(1))

        header.addLayout(header_text)
        header.addStretch()
        header.addWidget(new_button)

        layout.addLayout(header)

        self.recent_scans_table = QTableWidget(0, 5)
        self.recent_scans_table.setHorizontalHeaderLabels(
            ["ID", "TARGET", "PROFILE", "STATUS", "CREATED"]
        )
        self.recent_scans_table.setAlternatingRowColors(True)
        self.recent_scans_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.recent_scans_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.recent_scans_table.verticalHeader().setVisible(False)

        header_view = self.recent_scans_table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for column in (2, 3, 4):
            header_view.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )

        layout.addWidget(self.recent_scans_table)
        return panel

    def _create_placeholder_page(
        self,
        title: str,
        subtitle: str,
        feature_title: str,
        message: str,
        action_text: str,
    ) -> QWidget:
        page = QWidget()
        page.setObjectName("pageBackground")

        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("pageBackground")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(34, 28, 34, 34)
        layout.setSpacing(18)

        title_label = QLabel(title)
        title_label.setObjectName("accentHeading")
        title_label.setWordWrap(True)
        title_label.setMinimumHeight(52)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("pageSubtitle")
        subtitle_label.setWordWrap(True)
        subtitle_label.setMinimumHeight(42)

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        card = QFrame()
        card.setObjectName("contentCard")
        card.setMinimumHeight(520)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.MinimumExpanding,
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 38, 40, 38)
        card_layout.setSpacing(14)

        visual = QFrame()
        visual.setObjectName("brandIcon")
        visual.setFixedSize(96, 96)

        visual_layout = QVBoxLayout(visual)
        visual_layout.setContentsMargins(0, 0, 0, 0)

        visual_text = QLabel("X")
        visual_text.setObjectName("brandInitials")
        visual_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        visual_layout.addWidget(visual_text)

        heading = QLabel(feature_title)
        heading.setObjectName("accentHeading")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setWordWrap(True)
        heading.setMinimumHeight(74)

        message_label = QLabel(message)
        message_label.setObjectName("pageSubtitle")
        message_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        message_label.setWordWrap(True)
        message_label.setMaximumWidth(720)
        message_label.setMinimumHeight(110)
        message_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.MinimumExpanding,
        )

        action = QPushButton(action_text)
        action.setObjectName("accentButton")
        action.setEnabled(False)

        card_layout.addSpacing(18)
        card_layout.addWidget(visual, alignment=Qt.AlignmentFlag.AlignHCenter)
        card_layout.addSpacing(10)
        card_layout.addWidget(heading, alignment=Qt.AlignmentFlag.AlignHCenter)
        card_layout.addWidget(message_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        card_layout.addSpacing(8)
        card_layout.addWidget(action, alignment=Qt.AlignmentFlag.AlignHCenter)
        card_layout.addStretch(1)

        layout.addWidget(card)
        layout.addStretch(1)

        scroll.setWidget(content)
        outer.addWidget(scroll)
        return page

    def _create_settings_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("pageBackground")

        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content.setObjectName("pageBackground")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(34, 28, 34, 34)
        layout.setSpacing(18)

        title = QLabel("Application settings")
        title.setObjectName("accentHeading")
        title.setMinimumHeight(52)

        subtitle = QLabel(
            "Personalize XtremeCyber and prepare future assessment preferences."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        subtitle.setMinimumHeight(42)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)

        cards = [
            (
                "Appearance",
                "Switch between dark and light interface modes.",
                "Toggle Theme",
                self.theme_change_requested.emit,
            ),
            (
                "Scan preferences",
                "Thread limits, timeouts, and default profiles will appear here.",
                "Coming Soon",
                None,
            ),
            (
                "Critical alerts",
                "Configure email notifications for critical findings.",
                "Coming Soon",
                None,
            ),
            (
                "Local data",
                "Manage scan history, reports, and database maintenance.",
                "Coming Soon",
                None,
            ),
        ]

        for index, data in enumerate(cards):
            grid.addWidget(self._create_settings_card(*data), index // 2, index % 2)

        layout.addLayout(grid)
        layout.addStretch(1)

        scroll.setWidget(content)
        outer.addWidget(scroll)
        return page

    def _handle_scan_configuration(self, configuration) -> None:
        """Display feedback after successful configuration validation."""

        self.statusBar().showMessage(
        (
            f"Validated {configuration.target.normalized_value}: "
            f"{configuration.target.host_count} host(s), "
            f"{configuration.ports.count} TCP port(s)."
        ),
        6000,
    )

    def _handle_scan_completed(self, summary) -> None:
        """Display a message after the TCP scan finishes."""

        self.statusBar().showMessage(
        (
            f"TCP scan finished: "
            f"{summary.open_ports} open, "
            f"{summary.closed_ports} closed, "
            f"{summary.errors} errors."
        ),
        8000,
    )

    def _handle_scan_saved(
        self,
        scan_id: int,
    ) -> None:
        """Refresh the UI after a scan is saved."""

        self.results_page.refresh_history()
        self.results_page.select_scan(scan_id)
        self.refresh_dashboard()

        self.statusBar().showMessage(
            f"Scan #{scan_id} was saved to history.",
            7000,
        )

    @staticmethod
    def _create_settings_card(
        title: str,
        description: str,
        button_text: str,
        callback: Callable[[], None] | None,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")
        card.setMinimumHeight(220)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(23, 22, 23, 22)

        heading = QLabel(title)
        heading.setObjectName("sectionTitle")
        heading.setMinimumHeight(27)

        description_label = QLabel(description)
        description_label.setObjectName("sectionSubtitle")
        description_label.setWordWrap(True)
        description_label.setMinimumHeight(70)

        button = QPushButton(button_text)
        button.setObjectName("accentButton" if callback else "secondaryButton")

        if callback:
            button.clicked.connect(callback)
        else:
            button.setEnabled(False)

        layout.addWidget(heading)
        layout.addWidget(description_label)
        layout.addStretch()
        layout.addWidget(button)
        return card

    def _connect_signals(self) -> None:
        self.theme_button.clicked.connect(self.theme_change_requested.emit)

    def _create_navigation_handler(self, page_index: int) -> Callable[[], None]:
        return lambda: self.show_page(page_index)

    def show_page(self, page_index: int) -> None:
        if not 0 <= page_index < self.page_stack.count():
            return

        self.page_stack.setCurrentIndex(page_index)

        info = [
            ("Overview", "Security assessment activity at a glance"),
            ("New Scan", "Configure and launch an authorized assessment"),
            ("Results", "Review discovered hosts, services, and findings"),
            ("Reports", "Manage and export assessment documentation"),
            ("Settings", "Customize XtremeCyber preferences"),
            ("Users", "Create and manage XtremeCyber user accounts"),
        ]

        title, subtitle = info[page_index]
        self.top_page_title.setText(title)
        self.top_page_subtitle.setText(subtitle)

        for index, button in enumerate(self.navigation_buttons):
            button.setChecked(index == page_index)

        if page_index == 0:
            self.refresh_dashboard()

        if page_index == 2:
            self.results_page.refresh_history()

    def refresh_dashboard(self) -> None:
        """Refresh dashboard values from saved TCP scans."""

        try:
            stats = (
                self.scan_history_repository.dashboard_stats()
            )

            recent_scans = (
                self.scan_history_repository.get_recent(
                    limit=10
                )
            )

            self.total_scans_value.setText(
                str(stats["total"])
            )

            self.pending_scans_value.setText(
                str(stats["running"])
            )

            self.completed_scans_value.setText(
                str(stats["completed"])
            )

            self.database_status_value.setText(
                "Connected"
            )

            self._populate_recent_scans(
                recent_scans
            )

        except Exception as exc:
            logger.exception(
                "Could not refresh persisted scan dashboard."
            )

            self.database_status_value.setText(
                "Error"
            )

            self.statusBar().showMessage(
                f"Dashboard refresh failed: {exc}",
                5000,
            )

    def _populate_recent_scans(self, scans: list[dict]) -> None:
        self.recent_scans_table.setRowCount(len(scans))

        for row, scan in enumerate(scans):
            values = [
                str(scan.get("id", "")),
                str(scan.get("target", "")),
                str(scan.get("scan_type", "")).title(),
                str(scan.get("status", "")).title(),
                self._format_created_at(str(scan.get("created_at", ""))),
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in (0, 2, 3):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.recent_scans_table.setItem(row, column, item)

    def _handle_analysis_completed(self, summary) -> None:
        """Display feedback after post-scan exposure analysis."""

        highest = (
            summary.highest_severity.value.title()
            if summary.highest_severity is not None
            else "None"
        )

        self.statusBar().showMessage(
            (
                f"Vulnerability analysis completed for scan "
                f"#{summary.scan_id}: {summary.findings} finding(s), "
                f"highest severity {highest}."
            ),
            9000,
        )

        self.results_page.refresh_history()
        self.refresh_dashboard()

    @staticmethod
    def _format_created_at(value: str) -> str:
        if not value:
            return ""
        value = value.replace("T", " ")
        if "+" in value:
            value = value.split("+", maxsplit=1)[0]
        return value

    def set_active_theme(self, theme: Theme) -> None:
        self.theme_button.setText(
            "Light Mode" if theme == Theme.DARK else "Dark Mode"
        )

    def closeEvent(self, event) -> None:
        """Cancel a running scan before closing."""

        if hasattr(self, "scan_page"):
            self.scan_page.shutdown()

        super().closeEvent(event)
