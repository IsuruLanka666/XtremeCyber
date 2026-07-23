"""
Live TCP scan page with SQLite lifecycle persistence.

"""

from __future__ import annotations

import config as app_config

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.exceptions import XtremeCyberError
from core.logger import get_logger
from core.scanning.configuration import build_scan_configuration
from core.scanning.models import ScanConfiguration, ScanProfile
from core.scanning.persistence import (
    ScanRunRecorder,
    ScanRunRepository,
)
from core.scanning.profiles import PROFILE_LABELS
from core.scanning.results import (
    PortScanResult,
    PortState,
    ScanProgress,
    ScanSummary,
)
from core.vulnerability.service import (
    VulnerabilityAssessmentService,
)
from ui.scan_worker import ScanWorker


logger = get_logger(__name__)


class CleanTableDelegate(QStyledItemDelegate):
    """Remove Qt's native current-cell focus rectangle."""

    def paint(self, painter, option, index) -> None:
        clean_option = QStyleOptionViewItem(option)
        clean_option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, clean_option, index)


class ScanPage(QWidget):
    """Validate, execute, and persist an authorized TCP scan."""

    configuration_ready = Signal(object)
    scan_started = Signal(int)
    scan_saved = Signal(int)
    scan_completed = Signal(object)
    analysis_completed = Signal(object)

    def __init__(
        self,
        *,
        session=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.session = session
        self.repository = ScanRunRepository()

        self.vulnerability_service = (
            VulnerabilityAssessmentService(
                scan_repository=self.repository
            )
        )

        self.current_configuration: ScanConfiguration | None = None
        self.current_scan_id: int | None = None
        self.recorder: ScanRunRecorder | None = None

        self.scan_thread: QThread | None = None
        self.scan_worker: ScanWorker | None = None
        self.scan_running = False

        self.setObjectName("pageBackground")

        self._build_ui()
        self._update_profile_fields()
        self._set_controls_for_scan(False)

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        content.setObjectName("pageBackground")
        content.setMinimumWidth(930)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(34, 28, 34, 34)
        layout.setSpacing(16)

        layout.addLayout(self._create_header())

        top_row = QHBoxLayout()
        top_row.setSpacing(16)
        top_row.addWidget(self._create_configuration_card(), 3)
        top_row.addWidget(self._create_status_card(), 2)

        layout.addLayout(top_row)
        layout.addWidget(self._create_results_card(), 1)

        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)

    def _create_header(self) -> QHBoxLayout:
        header = QHBoxLayout()

        header_text = QVBoxLayout()
        header_text.setSpacing(3)

        title = QLabel("New security scan")
        title.setObjectName("accentHeading")
        title.setMinimumHeight(52)

        subtitle = QLabel(
            "Validate an authorized target and run a bounded, "
            "multithreaded TCP connect scan."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        subtitle.setMinimumHeight(42)

        header_text.addWidget(title)
        header_text.addWidget(subtitle)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("secondaryButton")
        self.reset_button.clicked.connect(self._reset_form)

        self.validate_button = QPushButton("Validate")
        self.validate_button.setObjectName("secondaryButton")
        self.validate_button.clicked.connect(
            self._validate_configuration
        )

        self.start_scan_button = QPushButton("Start Scan")
        self.start_scan_button.setObjectName("accentButton")
        self.start_scan_button.setEnabled(False)
        self.start_scan_button.clicked.connect(self._start_scan)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("secondaryButton")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_scan)

        header.addLayout(header_text)
        header.addStretch()
        header.addWidget(self.reset_button)
        header.addWidget(self.validate_button)
        header.addWidget(self.start_scan_button)
        header.addWidget(self.cancel_button)

        return header

    def _create_configuration_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")
        card.setMinimumHeight(400)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(13)

        title = QLabel("Scan configuration")
        title.setObjectName("sectionTitle")
        title.setMinimumHeight(28)

        description = QLabel(
            "Configure the authorized target, port profile, concurrency, "
            "and connection behavior."
        )
        description.setObjectName("sectionSubtitle")
        description.setWordWrap(True)
        description.setMinimumHeight(42)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText(
            "Hostname, IP address, or CIDR — e.g. 192.168.1.10"
        )
        self.target_input.setClearButtonEnabled(True)
        self.target_input.setMinimumHeight(42)

        self.profile_input = QComboBox()
        self.profile_input.setMinimumHeight(42)

        for profile in ScanProfile:
            self.profile_input.addItem(
                PROFILE_LABELS[profile],
                profile.value,
            )

        self.profile_input.setCurrentIndex(0)

        self.custom_ports_input = QLineEdit()
        self.custom_ports_input.setPlaceholderText(
            "Examples: 22,80,443 or 1-1024,8080"
        )
        self.custom_ports_input.setMinimumHeight(42)

        max_threads = max(
            1,
            int(getattr(app_config, "MAX_THREADS", 100)),
        )

        self.workers_input = QSpinBox()
        self.workers_input.setRange(1, min(max_threads, 200))
        self.workers_input.setValue(min(max_threads, 100))
        self.workers_input.setMinimumHeight(42)
        self.workers_input.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        default_timeout = float(
            getattr(app_config, "SCAN_TIMEOUT", 3)
        )

        self.timeout_input = QDoubleSpinBox()
        self.timeout_input.setRange(0.1, 30.0)
        self.timeout_input.setSingleStep(0.5)
        self.timeout_input.setDecimals(1)
        self.timeout_input.setSuffix(" seconds")
        self.timeout_input.setValue(default_timeout)
        self.timeout_input.setMinimumHeight(42)
        self.timeout_input.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.resolve_hostname_check = QCheckBox(
            "Resolve hostnames before scanning"
        )
        self.resolve_hostname_check.setChecked(True)

        self.banner_grab_check = QCheckBox(
            "Collect basic service banners"
        )
        self.banner_grab_check.setChecked(True)

        self.authorization_check = QCheckBox(
            "I confirm authorization to assess this target."
        )

        form = QFormLayout()
        form.setSpacing(12)
        form.setHorizontalSpacing(18)
        form.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )

        form.addRow("Target", self.target_input)
        form.addRow("Scan profile", self.profile_input)
        form.addRow("Custom TCP ports", self.custom_ports_input)
        form.addRow("Maximum workers", self.workers_input)
        form.addRow("Connection timeout", self.timeout_input)
        form.addRow("", self.resolve_hostname_check)
        form.addRow("", self.banner_grab_check)
        form.addRow("", self.authorization_check)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(form)
        layout.addStretch()

        self._connect_configuration_signals()

        return card

    def _create_status_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")
        card.setMinimumHeight(400)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(11)

        title = QLabel("Scan status")
        title.setObjectName("sectionTitle")
        title.setMinimumHeight(28)

        self.status_label = QLabel("Configuration not validated")
        self.status_label.setObjectName("pageSubtitle")
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(44)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(20)

        self.operations_label = self._status_label("Checks: 0 / 0")
        self.open_label = self._status_label("Open: 0")
        self.closed_label = self._status_label("Closed: 0")
        self.errors_label = self._status_label("Errors: 0")

        self.configuration_label = QLabel("Target: —\nPorts: —")
        self.configuration_label.setObjectName("pageSubtitle")
        self.configuration_label.setWordWrap(True)
        self.configuration_label.setMinimumHeight(88)

        layout.addWidget(title)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.operations_label)
        layout.addWidget(self.open_label)
        layout.addWidget(self.closed_label)
        layout.addWidget(self.errors_label)
        layout.addSpacing(8)
        layout.addWidget(self.configuration_label)
        layout.addStretch()

        return card

    def _create_results_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")
        card.setMinimumHeight(390)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title = QLabel("Live TCP results")
        title.setObjectName("sectionTitle")
        title.setMinimumHeight(28)

        subtitle = QLabel(
            "Open ports and connection errors are displayed by default."
        )
        subtitle.setObjectName("sectionSubtitle")
        subtitle.setWordWrap(True)
        subtitle.setMinimumHeight(24)

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        self.show_closed_check = QCheckBox(
            "Show closed ports during scan"
        )
        self.show_closed_check.setChecked(False)

        header.addLayout(title_layout)
        header.addStretch()
        header.addWidget(self.show_closed_check)

        self.results_table = QTableWidget(0, 7)
        self.results_table.setHorizontalHeaderLabels(
            [
                "HOST",
                "ADDRESS",
                "PORT",
                "STATE",
                "SERVICE",
                "LATENCY",
                "BANNER / ERROR",
            ]
        )
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setShowGrid(False)
        self.results_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.results_table.setItemDelegate(
            CleanTableDelegate(self.results_table)
        )
        self.results_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.results_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.results_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setMinimumHeight(260)

        table_header = self.results_table.horizontalHeader()

        for column in range(6):
            table_header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )

        table_header.setSectionResizeMode(
            6,
            QHeaderView.ResizeMode.Stretch,
        )

        layout.addLayout(header)
        layout.addWidget(self.results_table)

        return card

    def _connect_configuration_signals(self) -> None:
        self.profile_input.currentIndexChanged.connect(
            self._update_profile_fields
        )

        self.target_input.textChanged.connect(
            self._invalidate_configuration
        )
        self.profile_input.currentIndexChanged.connect(
            self._invalidate_configuration
        )
        self.custom_ports_input.textChanged.connect(
            self._invalidate_configuration
        )
        self.workers_input.valueChanged.connect(
            self._invalidate_configuration
        )
        self.timeout_input.valueChanged.connect(
            self._invalidate_configuration
        )
        self.resolve_hostname_check.toggled.connect(
            self._invalidate_configuration
        )
        self.banner_grab_check.toggled.connect(
            self._invalidate_configuration
        )
        self.authorization_check.toggled.connect(
            self._invalidate_configuration
        )

    @staticmethod
    def _status_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("pageSubtitle")
        label.setMinimumHeight(22)
        return label

    def _selected_profile(self) -> ScanProfile:
        data = self.profile_input.currentData()

        if data is None:
            return ScanProfile.QUICK

        return ScanProfile(str(data))

    def _update_profile_fields(self) -> None:
        is_custom = (
            self._selected_profile() == ScanProfile.CUSTOM
        )

        self.custom_ports_input.setEnabled(
            is_custom and not self.scan_running
        )

        if not is_custom:
            self.custom_ports_input.clear()

    def _invalidate_configuration(self, *args) -> None:
        if self.scan_running:
            return

        had_configuration = self.current_configuration is not None
        self.current_configuration = None
        self.start_scan_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

        if hasattr(self, "status_label"):
            self.status_label.setText(
                "Configuration changed — validate again"
                if had_configuration
                else "Configuration not validated"
            )

        if hasattr(self, "progress_bar"):
            self.progress_bar.setValue(0)

    def _build_configuration(self) -> ScanConfiguration:
        return build_scan_configuration(
            target_value=self.target_input.text(),
            profile=self._selected_profile(),
            custom_ports=self.custom_ports_input.text(),
            max_workers=self.workers_input.value(),
            timeout_seconds=self.timeout_input.value(),
            banner_grab=self.banner_grab_check.isChecked(),
            resolve_hostname=self.resolve_hostname_check.isChecked(),
            authorization_confirmed=self.authorization_check.isChecked(),
            worker_limit=min(
                int(getattr(app_config, "MAX_THREADS", 100)),
                200,
            ),
            max_network_hosts=int(
                getattr(app_config, "MAX_TARGETS_PER_SCAN", 256)
            ),
        )

    def _validate_configuration(self) -> None:
        if self.scan_running:
            return

        try:
            configuration = self._build_configuration()
        except XtremeCyberError as exc:
            self.current_configuration = None
            self.start_scan_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            self.status_label.setText("Validation failed")

            QMessageBox.warning(
                self,
                "Invalid Scan Configuration",
                str(exc),
            )
            return

        self.current_configuration = configuration
        self._show_configuration(configuration)
        self.start_scan_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.configuration_ready.emit(configuration)

    def _show_configuration(
        self,
        configuration: ScanConfiguration,
    ) -> None:
        total_operations = (
            configuration.target.host_count
            * configuration.ports.count
        )

        self.status_label.setText(
            "Configuration valid — ready to scan"
        )
        self.configuration_label.setText(
            (
                f"Target: {configuration.target.normalized_value}\n"
                f"Hosts: {configuration.target.host_count} | "
                f"Ports: {configuration.ports.count} | "
                f"Checks: {total_operations:,}\n"
                "History: the scan will be saved automatically."
            )
        )
        self.progress_bar.setValue(0)
        self.operations_label.setText(
            f"Checks: 0 / {total_operations:,}"
        )
        self.open_label.setText("Open: 0")
        self.closed_label.setText("Closed: 0")
        self.errors_label.setText("Errors: 0")

    def _start_scan(self) -> None:
        if self.scan_running:
            return

        if self.current_configuration is None:
            QMessageBox.information(
                self,
                "Validate Configuration",
                "Validate the scan configuration before starting.",
            )
            return

        try:
            configuration = self._build_configuration()
        except XtremeCyberError as exc:
            self.current_configuration = None
            self.start_scan_button.setEnabled(False)

            QMessageBox.warning(
                self,
                "Invalid Scan Configuration",
                str(exc),
            )
            return

        try:
            scan_id = self.repository.create_scan(
                configuration,
                user_id=(
                    int(self.session.user_id)
                    if self.session is not None
                    else None
                ),
            )
        except XtremeCyberError as exc:
            QMessageBox.critical(
                self,
                "Could Not Save Scan",
                str(exc),
            )
            return

        self.current_configuration = configuration
        self.current_scan_id = scan_id
        self.recorder = ScanRunRecorder(
            repository=self.repository,
            scan_id=scan_id,
            persist_closed_results=bool(
                getattr(
                    app_config,
                    "PERSIST_CLOSED_SCAN_RESULTS",
                    False,
                )
            ),
            progress_interval=int(
                getattr(
                    app_config,
                    "SCAN_PROGRESS_DB_INTERVAL",
                    50,
                )
            ),
        )

        self.results_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.configuration_label.setText(
            self.configuration_label.text()
            + f"\nSaved scan ID: {scan_id}"
        )

        self.scan_thread = QThread(self)
        self.scan_worker = ScanWorker(
            configuration,
            max_operations=int(
                getattr(app_config, "MAX_SCAN_OPERATIONS", 200_000)
            ),
            banner_max_bytes=int(
                getattr(app_config, "BANNER_MAX_BYTES", 256)
            ),
        )
        self.scan_worker.moveToThread(self.scan_thread)

        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.status_changed.connect(
            self.status_label.setText
        )
        self.scan_worker.progress_changed.connect(
            self._update_progress
        )
        self.scan_worker.result_ready.connect(
            self._handle_result
        )
        self.scan_worker.scan_finished.connect(
            self._scan_finished
        )
        self.scan_worker.scan_failed.connect(
            self._scan_failed
        )

        self.scan_worker.scan_finished.connect(
            self.scan_thread.quit
        )
        self.scan_worker.scan_failed.connect(
            self.scan_thread.quit
        )
        self.scan_thread.finished.connect(
            self._cleanup_scan_thread
        )

        self.scan_running = True
        self._set_controls_for_scan(True)
        self.scan_started.emit(scan_id)
        self.scan_thread.start()

    def _cancel_scan(self) -> None:
        if self.scan_worker is None:
            return

        self.status_label.setText("Cancellation requested...")
        self.scan_worker.cancel()
        self.cancel_button.setEnabled(False)

    def _update_progress(
        self,
        progress: ScanProgress,
    ) -> None:
        self.progress_bar.setValue(progress.percentage)
        self.operations_label.setText(
            f"Checks: {progress.completed:,} / {progress.total:,}"
        )
        self.open_label.setText(
            f"Open: {progress.open_ports}"
        )
        self.closed_label.setText(
            f"Closed: {progress.closed_ports}"
        )
        self.errors_label.setText(
            f"Errors: {progress.errors}"
        )

        if self.recorder is not None:
            try:
                self.recorder.record_progress(progress)
            except XtremeCyberError:
                logger.exception(
                    "Could not persist progress for scan id=%s.",
                    self.current_scan_id,
                )

    def _handle_result(
        self,
        result: PortScanResult,
    ) -> None:
        if self.recorder is not None:
            try:
                self.recorder.record_result(result)
            except XtremeCyberError:
                logger.exception(
                    "Could not persist result for scan id=%s.",
                    self.current_scan_id,
                )

        self._add_result_to_table(result)

    def _add_result_to_table(
        self,
        result: PortScanResult,
    ) -> None:
        should_display = (
            result.state != PortState.CLOSED
            or self.show_closed_check.isChecked()
        )

        if not should_display:
            return

        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        latency = (
            f"{result.latency_ms:.2f} ms"
            if result.latency_ms is not None
            else ""
        )
        detail = result.banner or result.error

        values = [
            result.host,
            result.resolved_address,
            str(result.port),
            result.state.value.title(),
            result.service,
            latency,
            detail,
        ]

        for column, value in enumerate(values):
            item = QTableWidgetItem(value)

            if column in (2, 3, 5):
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

            self.results_table.setItem(
                row,
                column,
                item,
            )

        self.results_table.scrollToBottom()

    def _scan_finished(
        self,
        summary: ScanSummary,
    ) -> None:
        self.scan_running = False
        self._set_controls_for_scan(False)

        persistence_error = ""

        if self.recorder is not None:
            try:
                self.recorder.complete(summary)
            except XtremeCyberError as exc:
                persistence_error = str(exc)
                logger.exception(
                    "Could not finalize scan id=%s.",
                    self.current_scan_id,
                )

        if summary.cancelled:
            self.status_label.setText(
                f"Scan cancelled at {summary.completion_percentage}% "
                f"after {summary.duration_seconds:.2f} seconds."
            )
        else:
            self.progress_bar.setValue(100)
            self.status_label.setText(
                f"Scan completed in "
                f"{summary.duration_seconds:.2f} seconds."
            )

        if persistence_error:
            QMessageBox.warning(
                self,
                "Scan Finished but Saving Failed",
                persistence_error,
            )

        if self.current_scan_id is not None:
            self.scan_saved.emit(self.current_scan_id)

        if self.current_scan_id is not None:
            try:
                assessment_summary = (
                    self.vulnerability_service.analyze_scan(
                        self.current_scan_id
                    )
                )
            except XtremeCyberError as exc:
                logger.exception(
                    "Could not analyze saved scan id=%s.",
                    self.current_scan_id,
                )

                QMessageBox.warning(
                    self,
                    "Scan Saved but Analysis Failed",
                    str(exc),
                )
            else:
                self.analysis_completed.emit(
                assessment_summary
                )

                self.status_label.setText(
                    (
                        f"Scan saved and analyzed: "
                        f"{assessment_summary.findings} finding(s), "
                        f"{assessment_summary.high} high, "
                        f"{assessment_summary.medium} medium."
                    )
                )
            

        self.scan_completed.emit(summary)

    def _scan_failed(self, message: str) -> None:
        self.scan_running = False
        self._set_controls_for_scan(False)
        self.status_label.setText("Scan failed")

        if self.recorder is not None:
            try:
                self.recorder.fail(message)
            except XtremeCyberError:
                logger.exception(
                    "Could not mark scan id=%s as failed.",
                    self.current_scan_id,
                )

        if self.current_scan_id is not None:
            self.scan_saved.emit(self.current_scan_id)

        QMessageBox.critical(
            self,
            "TCP Scan Failed",
            message,
        )

    def _cleanup_scan_thread(self) -> None:
        if self.scan_worker is not None:
            self.scan_worker.deleteLater()

        if self.scan_thread is not None:
            self.scan_thread.deleteLater()

        self.scan_worker = None
        self.scan_thread = None
        self.recorder = None

    def _set_controls_for_scan(self, running: bool) -> None:
        self.target_input.setEnabled(not running)
        self.profile_input.setEnabled(not running)
        self.custom_ports_input.setEnabled(
            not running
            and self._selected_profile() == ScanProfile.CUSTOM
        )
        self.workers_input.setEnabled(not running)
        self.timeout_input.setEnabled(not running)
        self.resolve_hostname_check.setEnabled(not running)
        self.banner_grab_check.setEnabled(not running)
        self.authorization_check.setEnabled(not running)

        self.validate_button.setEnabled(not running)
        self.reset_button.setEnabled(not running)

        self.start_scan_button.setEnabled(
            not running
            and self.current_configuration is not None
        )
        self.cancel_button.setEnabled(running)

    def _reset_form(self) -> None:
        if self.scan_running:
            return

        self.target_input.clear()
        self.profile_input.setCurrentIndex(0)
        self.custom_ports_input.clear()
        self.workers_input.setValue(
            min(
                int(getattr(app_config, "MAX_THREADS", 100)),
                100,
            )
        )
        self.timeout_input.setValue(
            float(getattr(app_config, "SCAN_TIMEOUT", 3))
        )
        self.resolve_hostname_check.setChecked(True)
        self.banner_grab_check.setChecked(True)
        self.authorization_check.setChecked(False)
        self.show_closed_check.setChecked(False)

        self.current_configuration = None
        self.current_scan_id = None
        self.recorder = None

        self.start_scan_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.status_label.setText("Configuration not validated")
        self.configuration_label.setText("Target: —\nPorts: —")
        self.progress_bar.setValue(0)
        self.operations_label.setText("Checks: 0 / 0")
        self.open_label.setText("Open: 0")
        self.closed_label.setText("Closed: 0")
        self.errors_label.setText("Errors: 0")
        self.results_table.setRowCount(0)

        self._update_profile_fields()

    def shutdown(self) -> None:
        """Request cancellation when the page/application is closing."""

        if self.scan_worker is not None:
            self.scan_worker.cancel()
