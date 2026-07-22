"""Scan configuration page for XtremeCyber"""

from __future__ import annotations

import config as app_config

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.exceptions import XtremeCyberError
from core.scanning.configuration import build_scan_configuration
from core.scanning.models import ScanConfiguration, ScanProfile
from core.scanning.profiles import PROFILE_LABELS


class ScanPage(QWidget):
    """Collect and validate a TCP scan configuration."""

    configuration_ready = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.current_configuration: ScanConfiguration | None = None
        self.setObjectName("pageBackground")

        self._build_ui()
        self._update_profile_fields()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 34)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(3)

        title = QLabel("New security scan")
        title.setObjectName("accentHeading")
        title.setMinimumHeight(52)

        subtitle = QLabel(
            "Validate an authorized target and prepare a safe TCP scan "
            "configuration."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        subtitle.setMinimumHeight(42)

        header_text.addWidget(title)
        header_text.addWidget(subtitle)

        reset_button = QPushButton("Reset")
        reset_button.setObjectName("secondaryButton")
        reset_button.clicked.connect(self._reset_form)

        validate_button = QPushButton("Validate Configuration")
        validate_button.setObjectName("accentButton")
        validate_button.clicked.connect(self._validate_configuration)

        header.addLayout(header_text)
        header.addStretch()
        header.addWidget(reset_button)
        header.addWidget(validate_button)

        layout.addLayout(header)

        content_row = QHBoxLayout()
        content_row.setSpacing(18)
        content_row.addWidget(self._create_configuration_card(), 3)
        content_row.addWidget(self._create_summary_card(), 2)

        layout.addLayout(content_row, 1)

    def _create_configuration_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(15)

        title = QLabel("Scan configuration")
        title.setObjectName("sectionTitle")

        description = QLabel(
            "This step validates the target and settings. The live network "
            "scanner is connected in Part 3 Step 2."
        )
        description.setObjectName("sectionSubtitle")
        description.setWordWrap(True)
        description.setMinimumHeight(44)

        form = QFormLayout()
        form.setSpacing(13)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText(
            "Hostname, IP, or CIDR — e.g. 192.168.1.10"
        )
        self.target_input.setClearButtonEnabled(True)

        self.profile_input = QComboBox()
        for profile in ScanProfile:
            self.profile_input.addItem(PROFILE_LABELS[profile], profile.value)
        self.profile_input.currentIndexChanged.connect(
            self._update_profile_fields
        )

        self.custom_ports_input = QLineEdit()
        self.custom_ports_input.setPlaceholderText(
            "Examples: 22,80,443 or 1-1024,8080"
        )

        max_threads = max(1, min(int(getattr(app_config, "MAX_THREADS", 100)), 200))

        self.workers_input = QSpinBox()
        self.workers_input.setRange(1, max_threads)
        self.workers_input.setValue(min(max_threads, 100))

        default_timeout = float(getattr(app_config, "SCAN_TIMEOUT", 3))
        default_timeout = min(max(default_timeout, 0.1), 30.0)

        self.timeout_input = QDoubleSpinBox()
        self.timeout_input.setRange(0.1, 30.0)
        self.timeout_input.setSingleStep(0.5)
        self.timeout_input.setDecimals(1)
        self.timeout_input.setSuffix(" seconds")
        self.timeout_input.setValue(default_timeout)

        self.resolve_hostname_check = QCheckBox(
            "Resolve hostnames before scanning"
        )
        self.resolve_hostname_check.setChecked(True)

        self.banner_grab_check = QCheckBox(
            "Attempt basic service banner collection"
        )
        self.banner_grab_check.setChecked(True)

        self.authorization_check = QCheckBox(
            "I own this target or have explicit permission to assess it."
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
        return card

    def _create_summary_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(13)

        title = QLabel("Validation summary")
        title.setObjectName("sectionTitle")

        description = QLabel(
            "Validate the form to review the normalized target and port set."
        )
        description.setObjectName("sectionSubtitle")
        description.setWordWrap(True)
        description.setMinimumHeight(44)

        self.validation_status = QLabel("Not validated")
        self.validation_status.setObjectName("cardValue")
        self.validation_status.setWordWrap(True)
        self.validation_status.setMinimumHeight(42)

        self.target_summary = self._summary_label("Target: —")
        self.kind_summary = self._summary_label("Target type: —")
        self.host_count_summary = self._summary_label("Hosts: —")
        self.profile_summary = self._summary_label("Profile: —")
        self.ports_summary = self._summary_label("Ports: —")
        self.workers_summary = self._summary_label("Workers: —")
        self.timeout_summary = self._summary_label("Timeout: —")

        start_button = QPushButton("Start Scan — available in Step 2")
        start_button.setObjectName("secondaryButton")
        start_button.setEnabled(False)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.validation_status)
        layout.addWidget(self.target_summary)
        layout.addWidget(self.kind_summary)
        layout.addWidget(self.host_count_summary)
        layout.addWidget(self.profile_summary)
        layout.addWidget(self.ports_summary)
        layout.addWidget(self.workers_summary)
        layout.addWidget(self.timeout_summary)
        layout.addStretch()
        layout.addWidget(start_button)
        return card

    @staticmethod
    def _summary_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("pageSubtitle")
        label.setWordWrap(True)
        label.setMinimumHeight(24)
        return label

    def _selected_profile(self) -> ScanProfile:
        return ScanProfile(str(self.profile_input.currentData()))

    def _update_profile_fields(self) -> None:
        is_custom = self._selected_profile() == ScanProfile.CUSTOM
        self.custom_ports_input.setEnabled(is_custom)
        if not is_custom:
            self.custom_ports_input.clear()

    def _validate_configuration(self) -> None:
        max_threads = max(1, min(int(getattr(app_config, "MAX_THREADS", 100)), 200))
        max_network_hosts = max(
            1,
            int(getattr(app_config, "MAX_TARGETS_PER_SCAN", 256)),
        )

        try:
            configuration = build_scan_configuration(
                target_value=self.target_input.text(),
                profile=self._selected_profile(),
                custom_ports=self.custom_ports_input.text(),
                max_workers=self.workers_input.value(),
                timeout_seconds=self.timeout_input.value(),
                banner_grab=self.banner_grab_check.isChecked(),
                resolve_hostname=self.resolve_hostname_check.isChecked(),
                authorization_confirmed=self.authorization_check.isChecked(),
                worker_limit=max_threads,
                max_network_hosts=max_network_hosts,
            )
        except XtremeCyberError as exc:
            self.current_configuration = None
            self.validation_status.setText("Validation failed")
            QMessageBox.warning(
                self,
                "Invalid Scan Configuration",
                str(exc),
            )
            return

        self.current_configuration = configuration
        self._show_configuration(configuration)
        self.configuration_ready.emit(configuration)

    def _show_configuration(self, configuration: ScanConfiguration) -> None:
        self.validation_status.setText("Configuration valid")
        self.target_summary.setText(
            f"Target: {configuration.target.normalized_value}"
        )
        self.kind_summary.setText(
            f"Target type: {configuration.target.kind.value.upper()}"
        )
        self.host_count_summary.setText(
            f"Hosts: {configuration.target.host_count}"
        )
        self.profile_summary.setText(
            f"Profile: {configuration.profile.value.title()}"
        )
        self.ports_summary.setText(
            f"TCP ports: {configuration.ports.normalized} "
            f"({configuration.ports.count} total)"
        )
        self.workers_summary.setText(
            f"Workers: {configuration.max_workers}"
        )
        self.timeout_summary.setText(
            f"Timeout: {configuration.timeout_seconds:.1f} seconds"
        )

    def _reset_form(self) -> None:
        self.target_input.clear()
        self.profile_input.setCurrentIndex(0)
        self.custom_ports_input.clear()

        max_threads = max(1, min(int(getattr(app_config, "MAX_THREADS", 100)), 200))
        self.workers_input.setValue(min(max_threads, 100))

        default_timeout = float(getattr(app_config, "SCAN_TIMEOUT", 3))
        self.timeout_input.setValue(min(max(default_timeout, 0.1), 30.0))

        self.resolve_hostname_check.setChecked(True)
        self.banner_grab_check.setChecked(True)
        self.authorization_check.setChecked(False)

        self.current_configuration = None
        self.validation_status.setText("Not validated")
        self.target_summary.setText("Target: —")
        self.kind_summary.setText("Target type: —")
        self.host_count_summary.setText("Hosts: —")
        self.profile_summary.setText("Profile: —")
        self.ports_summary.setText("Ports: —")
        self.workers_summary.setText("Workers: —")
        self.timeout_summary.setText("Timeout: —")
