"""
Persisted scan history and TCP findings
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.exceptions import XtremeCyberError
from core.scanning.persistence import ScanRunRepository


class CleanTableDelegate(QStyledItemDelegate):
    """Remove the native current-cell focus rectangle."""

    def paint(self, painter, option, index) -> None:
        clean_option = QStyleOptionViewItem(option)
        clean_option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, clean_option, index)


class ResultsPage(QWidget):
    """Browse persisted scan history and findings."""

    scan_selected = Signal(int)

    def __init__(
        self,
        *,
        session=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.session = session
        self.repository = ScanRunRepository()
        self.scans: list[dict[str, Any]] = []
        self.current_scan_id: int | None = None

        self.setObjectName("pageBackground")
        self._build_ui()
        self.refresh_history()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        content.setObjectName("pageBackground")
        content.setMinimumWidth(980)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(34, 28, 34, 34)
        layout.setSpacing(16)

        layout.addLayout(self._create_header())
        layout.addLayout(self._create_summary_row())
        layout.addWidget(self._create_history_card())
        layout.addWidget(self._create_findings_card(), 1)

        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _create_header(self) -> QHBoxLayout:
        header = QHBoxLayout()

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        title = QLabel("Assessment results")
        title.setObjectName("accentHeading")
        title.setMinimumHeight(52)

        subtitle = QLabel(
            "Browse saved scan history, status information, and "
            "persisted TCP findings."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        subtitle.setMinimumHeight(42)

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)

        refresh_button = QPushButton("Refresh")
        refresh_button.setObjectName("secondaryButton")
        refresh_button.clicked.connect(self.refresh_history)

        latest_button = QPushButton("Open Latest")
        latest_button.setObjectName("accentButton")
        latest_button.clicked.connect(self.open_latest_scan)

        header.addLayout(text_layout)
        header.addStretch()
        header.addWidget(refresh_button)
        header.addWidget(latest_button)

        return header

    def _create_summary_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(14)

        self.total_card = self._summary_card("Saved scans")
        self.completed_card = self._summary_card("Completed")
        self.open_ports_card = self._summary_card("Open ports")
        self.incomplete_card = self._summary_card("Incomplete")

        row.addWidget(self.total_card)
        row.addWidget(self.completed_card)
        row.addWidget(self.open_ports_card)
        row.addWidget(self.incomplete_card)

        return row

    @staticmethod
    def _summary_card(title: str) -> QFrame:
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

        value_label = QLabel("0")
        value_label.setObjectName("cardValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.value_label = value_label
        return card

    def _create_history_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")
        card.setMinimumHeight(285)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Scan history")
        title.setObjectName("sectionTitle")

        subtitle = QLabel(
            "Select a scan to load its stored TCP findings."
        )
        subtitle.setObjectName("sectionSubtitle")

        self.history_table = QTableWidget(0, 9)
        self.history_table.setHorizontalHeaderLabels(
            [
                "ID",
                "TARGET",
                "PROFILE",
                "STATUS",
                "HOSTS",
                "PORTS",
                "OPEN",
                "ERRORS",
                "STARTED",
            ]
        )
        self._configure_table(self.history_table)
        self.history_table.itemSelectionChanged.connect(
            self._history_selection_changed
        )

        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        for column in range(2, 9):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.history_table)

        return card

    def _create_findings_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("contentCard")
        card.setMinimumHeight(430)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title = QLabel("Stored findings")
        title.setObjectName("sectionTitle")

        self.findings_subtitle = QLabel(
            "Select a saved scan from the history table."
        )
        self.findings_subtitle.setObjectName("sectionSubtitle")
        self.findings_subtitle.setWordWrap(True)

        text_layout.addWidget(title)
        text_layout.addWidget(self.findings_subtitle)

        self.state_filter = QComboBox()
        self.state_filter.addItem("All stored states", "")
        self.state_filter.addItem("Open only", "open")
        self.state_filter.addItem("Errors only", "error")
        self.state_filter.addItem("Closed only", "closed")
        self.state_filter.setMinimumWidth(155)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search host, service, port, banner, or error"
        )
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumWidth(280)
        self.search_input.returnPressed.connect(
            self.refresh_findings
        )

        filter_button = QPushButton("Apply")
        filter_button.setObjectName("secondaryButton")
        filter_button.clicked.connect(self.refresh_findings)

        header.addLayout(text_layout)
        header.addStretch()
        header.addWidget(self.state_filter)
        header.addWidget(self.search_input)
        header.addWidget(filter_button)

        self.findings_table = QTableWidget(0, 8)
        self.findings_table.setHorizontalHeaderLabels(
            [
                "HOST",
                "ADDRESS",
                "PORT",
                "STATE",
                "SERVICE",
                "LATENCY",
                "BANNER / ERROR",
                "SCANNED",
            ]
        )
        self._configure_table(self.findings_table)

        findings_header = self.findings_table.horizontalHeader()

        for column in range(6):
            findings_header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )

        findings_header.setSectionResizeMode(
            6,
            QHeaderView.ResizeMode.Stretch,
        )
        findings_header.setSectionResizeMode(
            7,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        layout.addLayout(header)
        layout.addWidget(self.findings_table)

        return card

    @staticmethod
    def _configure_table(table: QTableWidget) -> None:
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setItemDelegate(CleanTableDelegate(table))
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        table.verticalHeader().setVisible(False)

    def refresh_history(self) -> None:
        try:
            self.scans = self.repository.get_recent_scans(
                limit=250
            )
            stats = self.repository.dashboard_stats()
        except XtremeCyberError as exc:
            QMessageBox.critical(
                self,
                "Could Not Load Scan History",
                str(exc),
            )
            return

        self.total_card.value_label.setText(
            str(stats["total"])
        )
        self.completed_card.value_label.setText(
            str(stats["completed"])
        )
        self.open_ports_card.value_label.setText(
            str(stats["open_ports"])
        )
        self.incomplete_card.value_label.setText(
            str(stats["incomplete"] + stats["running"])
        )

        self.history_table.setRowCount(len(self.scans))

        for row, scan in enumerate(self.scans):
            values = [
                str(scan["id"]),
                str(scan["target"]),
                str(scan["profile"]).title(),
                str(scan["status"]).title(),
                str(scan["host_count"]),
                str(scan["port_count"]),
                str(scan["open_ports"]),
                str(scan["errors"]),
                self._format_time(scan["started_at"]),
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)

                if column in (0, 2, 3, 4, 5, 6, 7):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.history_table.setItem(
                    row,
                    column,
                    item,
                )

        if self.current_scan_id is not None:
            self.select_scan(self.current_scan_id)

    def open_latest_scan(self) -> None:
        if not self.scans:
            QMessageBox.information(
                self,
                "No Saved Scans",
                "No persisted scans are available yet.",
            )
            return

        self.select_scan(int(self.scans[0]["id"]))

    def select_scan(self, scan_id: int) -> None:
        for row, scan in enumerate(self.scans):
            if int(scan["id"]) != int(scan_id):
                continue

            self.history_table.selectRow(row)
            self.history_table.scrollToItem(
                self.history_table.item(row, 0)
            )
            self.current_scan_id = int(scan_id)
            self.refresh_findings()
            return

        self.current_scan_id = int(scan_id)
        self.refresh_history()

    def _history_selection_changed(self) -> None:
        row = self.history_table.currentRow()

        if row < 0 or row >= len(self.scans):
            return

        self.current_scan_id = int(self.scans[row]["id"])
        self.refresh_findings()
        self.scan_selected.emit(self.current_scan_id)

    def refresh_findings(self) -> None:
        if self.current_scan_id is None:
            self.findings_table.setRowCount(0)
            self.findings_subtitle.setText(
                "Select a saved scan from the history table."
            )
            return

        state = str(self.state_filter.currentData() or "")
        states = (state,) if state else ()

        try:
            scan = self.repository.get_scan(
                self.current_scan_id
            )
            findings = self.repository.get_results(
                self.current_scan_id,
                states=states,
                search=self.search_input.text(),
                limit=5000,
            )
            counts = self.repository.result_counts(
                self.current_scan_id
            )
        except XtremeCyberError as exc:
            QMessageBox.warning(
                self,
                "Could Not Load Findings",
                str(exc),
            )
            return

        if scan is None:
            self.findings_table.setRowCount(0)
            self.findings_subtitle.setText(
                "The selected scan no longer exists."
            )
            return

        self.findings_subtitle.setText(
            (
                f"Scan #{scan['id']} — {scan['target']} — "
                f"{scan['status'].title()} — "
                f"{counts['stored']} stored finding(s)"
            )
        )

        self.findings_table.setRowCount(len(findings))

        for row, finding in enumerate(findings):
            latency = (
                f"{float(finding['latency_ms']):.2f} ms"
                if finding["latency_ms"] is not None
                else ""
            )
            detail = (
                str(finding["banner"] or "")
                or str(finding["error"] or "")
            )

            values = [
                str(finding["host"]),
                str(finding["resolved_address"] or ""),
                str(finding["port"]),
                str(finding["state"]).title(),
                str(finding["service"] or "unknown"),
                latency,
                detail,
                self._format_time(finding["scanned_at"]),
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)

                if column in (2, 3, 5):
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.findings_table.setItem(
                    row,
                    column,
                    item,
                )

    @staticmethod
    def _format_time(value: object) -> str:
        if not value:
            return "—"

        formatted = str(value).replace("T", " ")

        if "+" in formatted:
            formatted = formatted.split("+", maxsplit=1)[0]

        return formatted
