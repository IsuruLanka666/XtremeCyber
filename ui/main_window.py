"""
Main user interface for XtremeCyber.
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


logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main XtremeCyber desktop window."""

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
        self.setMinimumSize(1120, 720)

        self._build_ui()
        self._connect_signals()
        self.show_page(0)
        self.refresh_dashboard()
        self.statusBar().showMessage(f"{APP_NAME} {VERSION} ready", 5000)

    def _build_ui(self) -> None:
        application_root = QWidget()
        application_root.setObjectName("applicationRoot")
        self.setCentralWidget(application_root)

        root_layout = QHBoxLayout(application_root)
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
        self.page_stack.addWidget(
            self._create_placeholder_page(
                title="New security scan",
                subtitle=(
                    "Configure an authorized target and select a scanning profile."
                ),
                feature_title="Scanning workspace",
                message=(
                    "Target entry, scan profiles, port settings, progress "
                    "monitoring, and the scanning engine will be connected "
                    "in the scanning development phase."
                ),
                action_text="Prepare Scan",
            )
        )
        self.page_stack.addWidget(
            self._create_placeholder_page(
                title="Assessment results",
                subtitle=(
                    "Analyze discovered hosts, services, ports, and vulnerability findings."
                ),
                feature_title="Unified result explorer",
                message=(
                    "Filtering, severity indicators, host details, service "
                    "information, and CVE results will be implemented in "
                    "the results phase."
                ),
                action_text="Refresh Results",
            )
        )
        self.page_stack.addWidget(
            self._create_placeholder_page(
                title="Security reports",
                subtitle="Create clear reports for completed assessments.",
                feature_title="Professional report centre",
                message=(
                    "PDF, CSV, and JSON exports, report previews, saved "
                    "reports, and download management will be implemented "
                    "during the reporting phase."
                ),
                action_text="View Reports",
            )
        )
        self.page_stack.addWidget(self._create_settings_page())

        main_layout.addWidget(self.page_stack, 1)
        root_layout.addWidget(main_area, 1)

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(245)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(19, 24, 19, 20)
        layout.setSpacing(9)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)

        brand_icon = QFrame()
        brand_icon.setObjectName("brandIcon")
        brand_icon.setFixedSize(52, 52)

        icon_layout = QVBoxLayout(brand_icon)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        initials = QLabel("XC")
        initials.setObjectName("brandInitials")
        initials.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(initials)

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(1)

        application_title = QLabel(APP_NAME)
        application_title.setObjectName("applicationTitle")

        application_subtitle = QLabel("Security workspace")
        application_subtitle.setObjectName("applicationSubtitle")

        brand_text_layout.addWidget(application_title)
        brand_text_layout.addWidget(application_subtitle)

        brand_row.addWidget(brand_icon)
        brand_row.addLayout(brand_text_layout)
        brand_row.addStretch()

        layout.addLayout(brand_row)
        layout.addSpacing(30)

        workspace_label = QLabel("WORKSPACE")
        workspace_label.setObjectName("navigationSectionLabel")
        layout.addWidget(workspace_label)
        layout.addSpacing(3)

        for text, page_index in [
            ("Overview", 0),
            ("New Scan", 1),
            ("Results", 2),
            ("Reports", 3),
        ]:
            layout.addWidget(
                self._create_navigation_button(text, page_index)
            )

        layout.addSpacing(19)

        application_label = QLabel("APPLICATION")
        application_label.setObjectName("navigationSectionLabel")
        layout.addWidget(application_label)
        layout.addSpacing(3)
        layout.addWidget(self._create_navigation_button("Settings", 4))
        layout.addStretch()

        security_card = QFrame()
        security_card.setObjectName("compactInfoCard")

        security_layout = QVBoxLayout(security_card)
        security_layout.setContentsMargins(15, 15, 15, 15)
        security_layout.setSpacing(5)

        security_title = QLabel("Authorized access")
        security_title.setObjectName("sectionTitle")

        security_message = QLabel(
            "Only assess systems you own or have explicit permission to test."
        )
        security_message.setObjectName("sectionSubtitle")
        security_message.setWordWrap(True)

        version_label = QLabel(f"XtremeCyber {VERSION}")
        version_label.setObjectName("applicationSubtitle")

        security_layout.addWidget(security_title)
        security_layout.addWidget(security_message)
        security_layout.addSpacing(7)
        security_layout.addWidget(version_label)

        layout.addWidget(security_card)
        return sidebar

    def _create_navigation_button(
        self,
        text: str,
        page_index: int,
    ) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("navigationButton")
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(
            self._create_navigation_handler(page_index)
        )
        self.navigation_buttons.append(button)
        return button

    def _create_top_bar(self) -> QFrame:
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(88)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(31, 15, 31, 10)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        self.top_page_title = QLabel("Overview")
        self.top_page_title.setObjectName("topPageTitle")

        self.top_page_subtitle = QLabel(
            "Security assessment activity at a glance"
        )
        self.top_page_subtitle.setObjectName("topPageSubtitle")

        title_layout.addWidget(self.top_page_title)
        title_layout.addWidget(self.top_page_subtitle)

        layout.addLayout(title_layout)
        layout.addStretch()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("secondaryButton")
        self.refresh_button.clicked.connect(self.refresh_dashboard)

        self.theme_button = QPushButton("Light Mode")
        self.theme_button.setObjectName("accentButton")

        layout.addWidget(self.refresh_button)
        layout.addWidget(self.theme_button)
        return top_bar

    def _create_dashboard_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("pageBackground")

        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        content.setObjectName("pageBackground")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(31, 17, 31, 31)
        layout.setSpacing(21)

        page_title = QLabel("Security overview")
        page_title.setObjectName("pageTitle")

        page_subtitle = QLabel(
            "Monitor assessments, view scan activity, and begin a new "
            "authorized vulnerability evaluation."
        )
        page_subtitle.setObjectName("pageSubtitle")
        page_subtitle.setWordWrap(True)

        layout.addWidget(page_title)
        layout.addWidget(page_subtitle)
        layout.addWidget(self._create_hero_panel())

        self.total_scans_value = QLabel("0")
        self.pending_scans_value = QLabel("0")
        self.completed_scans_value = QLabel("0")
        self.database_status_value = QLabel("Connected")

        card_grid = QGridLayout()
        card_grid.setHorizontalSpacing(15)
        card_grid.setVerticalSpacing(15)

        card_data = [
            ("Total assessments", self.total_scans_value, "All stored vulnerability scans", "SC", "statIconBlue"),
            ("Waiting scans", self.pending_scans_value, "Assessments pending execution", "PD", "statIconPurple"),
            ("Completed", self.completed_scans_value, "Successfully completed scans", "OK", "statIconGreen"),
            ("Data storage", self.database_status_value, "Local SQLite storage layer", "DB", "statIconOrange"),
        ]

        for index, data in enumerate(card_data):
            card_grid.addWidget(self._create_stat_card(*data), 0, index)
            card_grid.setColumnStretch(index, 1)

        layout.addLayout(card_grid)
        layout.addWidget(self._create_recent_scans_panel(), 1)

        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)
        return page

    def _create_hero_panel(self) -> QFrame:
        hero_panel = QFrame()
        hero_panel.setObjectName("heroPanel")
        hero_panel.setMinimumHeight(205)

        layout = QHBoxLayout(hero_panel)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(20)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(9)

        badge = QLabel("XTREMECYBER ASSESSMENT CENTRE")
        badge.setObjectName("heroBadge")
        badge.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed,
        )

        title = QLabel(
            "Understand your attack surface\nbefore someone else does."
        )
        title.setObjectName("heroTitle")

        description = QLabel(
            "Launch structured vulnerability assessments, organize findings, "
            "and build clear defensive reports from one workspace."
        )
        description.setObjectName("heroDescription")
        description.setWordWrap(True)
        description.setMaximumWidth(640)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        start_button = QPushButton("Start New Scan")
        start_button.setObjectName("primaryButton")
        start_button.clicked.connect(lambda: self.show_page(1))

        results_button = QPushButton("Review Results")
        results_button.setObjectName("secondaryButton")
        results_button.clicked.connect(lambda: self.show_page(2))

        action_row.addWidget(start_button)
        action_row.addWidget(results_button)
        action_row.addStretch()

        content_layout.addWidget(badge)
        content_layout.addWidget(title)
        content_layout.addWidget(description)
        content_layout.addStretch()
        content_layout.addLayout(action_row)

        decoration_area = QFrame()
        decoration_area.setFixedWidth(230)

        decoration_layout = QGridLayout(decoration_area)
        decoration_layout.setContentsMargins(15, 8, 0, 8)

        decoration_one = QFrame()
        decoration_one.setObjectName("heroDecorationOne")
        decoration_one.setFixedSize(105, 105)

        decoration_one_layout = QVBoxLayout(decoration_one)
        decoration_one_layout.setContentsMargins(0, 0, 0, 0)

        decoration_text = QLabel("XC")
        decoration_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        decoration_text.setStyleSheet(
            "color: white; font-size: 28px; font-weight: 800;"
        )
        decoration_one_layout.addWidget(decoration_text)

        decoration_two = QFrame()
        decoration_two.setObjectName("heroDecorationTwo")
        decoration_two.setFixedSize(70, 70)

        small_text_layout = QVBoxLayout(decoration_two)
        small_text_layout.setContentsMargins(0, 0, 0, 0)

        secure_text = QLabel("✓")
        secure_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        secure_text.setStyleSheet(
            "color: white; font-size: 27px; font-weight: 800;"
        )
        small_text_layout.addWidget(secure_text)

        decoration_layout.addWidget(
            decoration_one,
            0,
            0,
            2,
            2,
            Qt.AlignmentFlag.AlignCenter,
        )
        decoration_layout.addWidget(
            decoration_two,
            1,
            1,
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignBottom,
        )

        layout.addLayout(content_layout, 1)
        layout.addWidget(decoration_area)
        return hero_panel

    @staticmethod
    def _create_stat_card(
        title: str,
        value_label: QLabel,
        description: str,
        icon_text: str,
        icon_object_name: str,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(160)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 17, 18, 17)
        layout.setSpacing(8)

        top_row = QHBoxLayout()

        icon_frame = QFrame()
        icon_frame.setObjectName(icon_object_name)
        icon_frame.setFixedSize(45, 45)

        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon_text)
        icon_label.setObjectName("statIconText")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)

        top_row.addWidget(icon_frame)
        top_row.addStretch()

        value_label.setObjectName("cardValue")

        description_label = QLabel(description)
        description_label.setObjectName("cardDescription")
        description_label.setWordWrap(True)

        layout.addLayout(top_row)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(description_label)
        return card

    def _create_recent_scans_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("contentCard")
        panel.setMinimumHeight(330)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(21, 20, 21, 21)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(2)

        title = QLabel("Recent assessments")
        title.setObjectName("sectionTitle")

        subtitle = QLabel(
            "Latest vulnerability scans stored in your local workspace."
        )
        subtitle.setObjectName("sectionSubtitle")

        header_text_layout.addWidget(title)
        header_text_layout.addWidget(subtitle)

        start_scan_button = QPushButton("New Assessment")
        start_scan_button.setObjectName("accentButton")
        start_scan_button.clicked.connect(lambda: self.show_page(1))

        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()
        header_layout.addWidget(start_scan_button)

        layout.addLayout(header_layout)

        self.recent_scans_table = QTableWidget(0, 5)
        self.recent_scans_table.setHorizontalHeaderLabels(
            ["ID", "TARGET", "PROFILE", "STATUS", "CREATED"]
        )
        self.recent_scans_table.setAlternatingRowColors(True)
        self.recent_scans_table.setShowGrid(False)
        self.recent_scans_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.recent_scans_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.recent_scans_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.recent_scans_table.verticalHeader().setVisible(False)

        header = self.recent_scans_table.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            4,
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

        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        content.setObjectName("pageBackground")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(31, 20, 31, 31)
        layout.setSpacing(19)

        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        title_label.setWordWrap(True)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("pageSubtitle")
        subtitle_label.setWordWrap(True)
        subtitle_label.setMinimumHeight(
            subtitle_label.sizeHint().height()
        )

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        feature_card = QFrame()
        feature_card.setObjectName("contentCard")
        feature_card.setMinimumHeight(460)

        feature_layout = QVBoxLayout(feature_card)
        feature_layout.setContentsMargins(35, 32, 35, 32)
        feature_layout.setSpacing(12)

        visual_mark = QFrame()
        visual_mark.setObjectName("brandIcon")
        visual_mark.setFixedSize(76, 76)

        visual_layout = QVBoxLayout(visual_mark)
        visual_layout.setContentsMargins(0, 0, 0, 0)

        visual_text = QLabel("XC")
        visual_text.setObjectName("brandInitials")
        visual_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        visual_layout.addWidget(visual_text)

        feature_heading = QLabel(feature_title)
        feature_heading.setObjectName("pageTitle")
        feature_heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        feature_heading.setWordWrap(True)
        feature_heading.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        feature_heading.setMinimumHeight(
            feature_heading.sizeHint().height()
        )

        feature_description = QLabel(message)
        feature_description.setObjectName("pageSubtitle")
        feature_description.setAlignment(
            Qt.AlignmentFlag.AlignHCenter
            | Qt.AlignmentFlag.AlignTop
        )
        feature_description.setWordWrap(True)
        feature_description.setMaximumWidth(700)
        feature_description.setMinimumHeight(90)
        feature_description.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.MinimumExpanding,
        )

        action_button = QPushButton(action_text)
        action_button.setObjectName("accentButton")
        action_button.setEnabled(False)

        feature_layout.addStretch(1)
        feature_layout.addWidget(
            visual_mark,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        feature_layout.addSpacing(12)
        feature_layout.addWidget(
            feature_heading,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        feature_layout.addSpacing(8)
        feature_layout.addWidget(
            feature_description,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        feature_layout.addSpacing(18)
        feature_layout.addWidget(
            action_button,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        feature_layout.addStretch(1)

        layout.addWidget(feature_card, 1)

        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)
        return page

    def _create_settings_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("pageBackground")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(31, 20, 31, 31)
        layout.setSpacing(19)

        title = QLabel("Application settings")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Personalize XtremeCyber appearance and prepare future "
            "assessment preferences."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        settings_grid = QGridLayout()
        settings_grid.setSpacing(16)

        settings_grid.addWidget(
            self._create_settings_card(
                "Appearance",
                "Switch between dark and light interface modes. "
                "Your selected theme is stored automatically.",
                "Toggle Theme",
                self.theme_change_requested.emit,
            ),
            0,
            0,
        )
        settings_grid.addWidget(
            self._create_settings_card(
                "Scan preferences",
                "Thread limits, timeout values, port profiles, and default "
                "scan behavior will appear here.",
                "Coming Soon",
                None,
            ),
            0,
            1,
        )
        settings_grid.addWidget(
            self._create_settings_card(
                "Critical alerts",
                "Configure email notification settings for critical "
                "vulnerability findings.",
                "Coming Soon",
                None,
            ),
            1,
            0,
        )
        settings_grid.addWidget(
            self._create_settings_card(
                "Local data",
                "Manage scan history, generated reports, and database "
                "maintenance operations.",
                "Coming Soon",
                None,
            ),
            1,
            1,
        )

        settings_grid.setColumnStretch(0, 1)
        settings_grid.setColumnStretch(1, 1)

        layout.addLayout(settings_grid)
        layout.addStretch()
        return page

    @staticmethod
    def _create_settings_card(
        title: str,
        description: str,
        button_text: str,
        callback: Callable[[], None] | None,
    ) -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")
        card.setMinimumHeight(210)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(23, 22, 23, 22)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")

        description_label = QLabel(description)
        description_label.setObjectName("sectionSubtitle")
        description_label.setWordWrap(True)
        description_label.setMinimumHeight(55)

        action_button = QPushButton(button_text)
        action_button.setObjectName(
            "accentButton"
            if callback is not None
            else "secondaryButton"
        )

        if callback is not None:
            action_button.clicked.connect(callback)
        else:
            action_button.setEnabled(False)

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()
        layout.addWidget(action_button)
        return card

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
        if page_index < 0 or page_index >= self.page_stack.count():
            return

        self.page_stack.setCurrentIndex(page_index)

        page_information = [
            ("Overview", "Security assessment activity at a glance"),
            ("New Scan", "Configure and launch an authorized assessment"),
            ("Results", "Review discovered hosts, services, and findings"),
            ("Reports", "Manage and export assessment documentation"),
            ("Settings", "Customize XtremeCyber preferences"),
        ]

        title, subtitle = page_information[page_index]
        self.top_page_title.setText(title)
        self.top_page_subtitle.setText(subtitle)

        for index, button in enumerate(self.navigation_buttons):
            button.setChecked(index == page_index)

        if page_index == 0:
            self.refresh_dashboard()

    def refresh_dashboard(self) -> None:
        try:
            all_scans = self.scan_repository.get_recent(limit=100)
            total_scans = self.scan_repository.count_all()

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

            self._populate_recent_scans(
                self.scan_repository.get_recent(limit=10)
            )

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
                self._format_created_at(
                    str(scan.get("created_at", ""))
                ),
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)

                if column_index in (0, 2, 3):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.recent_scans_table.setItem(
                    row_index,
                    column_index,
                    item,
                )

    @staticmethod
    def _format_created_at(value: str) -> str:
        if not value:
            return ""

        formatted = value.replace("T", " ")

        if "+" in formatted:
            formatted = formatted.split("+", maxsplit=1)[0]

        return formatted

    def set_active_theme(self, theme: Theme) -> None:
        self.theme_button.setText(
            "Light Mode"
            if theme == Theme.DARK
            else "Dark Mode"
        )
