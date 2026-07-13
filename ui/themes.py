"""
Theme management for the XtremeCyber desktop application.
"""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from core.constants import Theme


DARK_STYLESHEET = """
QWidget {
    background-color: #111827;
    color: #F9FAFB;
    font-family: "Segoe UI";
    font-size: 14px;
}

QMainWindow {
    background-color: #0B1120;
}

QFrame#sidebar {
    background-color: #0F172A;
    border-right: 1px solid #263244;
}

QFrame#topBar {
    background-color: #111827;
    border-bottom: 1px solid #263244;
}

QFrame#contentFrame {
    background-color: #111827;
}

QFrame#statCard,
QFrame#panelCard {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
}

QLabel#applicationTitle {
    color: #22D3EE;
    font-size: 22px;
    font-weight: 700;
}

QLabel#pageTitle {
    color: #F8FAFC;
    font-size: 26px;
    font-weight: 700;
}

QLabel#pageSubtitle {
    color: #94A3B8;
    font-size: 13px;
}

QLabel#cardTitle {
    color: #94A3B8;
    font-size: 13px;
    font-weight: 600;
}

QLabel#cardValue {
    color: #F8FAFC;
    font-size: 28px;
    font-weight: 700;
}

QLabel#sectionTitle {
    color: #F8FAFC;
    font-size: 17px;
    font-weight: 700;
}

QLabel#placeholderText {
    color: #94A3B8;
    font-size: 15px;
}

QPushButton {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 9px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #26364A;
    border-color: #22D3EE;
}

QPushButton:pressed {
    background-color: #0E7490;
}

QPushButton#navigationButton {
    background-color: transparent;
    color: #CBD5E1;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
}

QPushButton#navigationButton:hover {
    background-color: #1E293B;
    color: #FFFFFF;
}

QPushButton#navigationButton:checked {
    background-color: #164E63;
    color: #67E8F9;
    border-left: 3px solid #22D3EE;
}

QPushButton#primaryButton {
    background-color: #0891B2;
    color: #FFFFFF;
    border: none;
    padding: 10px 18px;
}

QPushButton#primaryButton:hover {
    background-color: #06B6D4;
}

QPushButton#dangerButton {
    background-color: #991B1B;
    color: #FFFFFF;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #B91C1C;
}

QLineEdit,
QComboBox,
QSpinBox {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 7px;
    padding: 8px;
    selection-background-color: #0891B2;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus {
    border: 1px solid #22D3EE;
}

QTableWidget {
    background-color: #0F172A;
    alternate-background-color: #172033;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: #334155;
    selection-background-color: #164E63;
}

QHeaderView::section {
    background-color: #1E293B;
    color: #CBD5E1;
    border: none;
    border-bottom: 1px solid #334155;
    padding: 9px;
    font-weight: 600;
}

QTableCornerButton::section {
    background-color: #1E293B;
    border: none;
}

QProgressBar {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 6px;
    text-align: center;
    min-height: 18px;
}

QProgressBar::chunk {
    background-color: #06B6D4;
    border-radius: 5px;
}

QScrollBar:vertical {
    background-color: #0F172A;
    width: 11px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #475569;
    border-radius: 5px;
    min-height: 25px;
}

QScrollBar::handle:vertical:hover {
    background-color: #64748B;
}

QStatusBar {
    background-color: #0F172A;
    color: #94A3B8;
    border-top: 1px solid #263244;
}
"""


LIGHT_STYLESHEET = """
QWidget {
    background-color: #F1F5F9;
    color: #0F172A;
    font-family: "Segoe UI";
    font-size: 14px;
}

QMainWindow {
    background-color: #E2E8F0;
}

QFrame#sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #CBD5E1;
}

QFrame#topBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #CBD5E1;
}

QFrame#contentFrame {
    background-color: #F1F5F9;
}

QFrame#statCard,
QFrame#panelCard {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 12px;
}

QLabel#applicationTitle {
    color: #0369A1;
    font-size: 22px;
    font-weight: 700;
}

QLabel#pageTitle {
    color: #0F172A;
    font-size: 26px;
    font-weight: 700;
}

QLabel#pageSubtitle {
    color: #64748B;
    font-size: 13px;
}

QLabel#cardTitle {
    color: #64748B;
    font-size: 13px;
    font-weight: 600;
}

QLabel#cardValue {
    color: #0F172A;
    font-size: 28px;
    font-weight: 700;
}

QLabel#sectionTitle {
    color: #0F172A;
    font-size: 17px;
    font-weight: 700;
}

QLabel#placeholderText {
    color: #64748B;
    font-size: 15px;
}

QPushButton {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 9px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #E0F2FE;
    border-color: #0284C7;
}

QPushButton:pressed {
    background-color: #BAE6FD;
}

QPushButton#navigationButton {
    background-color: transparent;
    color: #334155;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
}

QPushButton#navigationButton:hover {
    background-color: #E0F2FE;
    color: #075985;
}

QPushButton#navigationButton:checked {
    background-color: #BAE6FD;
    color: #075985;
    border-left: 3px solid #0284C7;
}

QPushButton#primaryButton {
    background-color: #0284C7;
    color: #FFFFFF;
    border: none;
    padding: 10px 18px;
}

QPushButton#primaryButton:hover {
    background-color: #0369A1;
}

QLineEdit,
QComboBox,
QSpinBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 7px;
    padding: 8px;
    selection-background-color: #0284C7;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus {
    border: 1px solid #0284C7;
}

QTableWidget {
    background-color: #FFFFFF;
    alternate-background-color: #F8FAFC;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    gridline-color: #E2E8F0;
    selection-background-color: #BAE6FD;
}

QHeaderView::section {
    background-color: #E2E8F0;
    color: #334155;
    border: none;
    border-bottom: 1px solid #CBD5E1;
    padding: 9px;
    font-weight: 600;
}

QTableCornerButton::section {
    background-color: #E2E8F0;
    border: none;
}

QProgressBar {
    background-color: #E2E8F0;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    text-align: center;
    min-height: 18px;
}

QProgressBar::chunk {
    background-color: #0284C7;
    border-radius: 5px;
}

QStatusBar {
    background-color: #FFFFFF;
    color: #64748B;
    border-top: 1px solid #CBD5E1;
}
"""


class ThemeManager:
    """Apply and track the active XtremeCyber theme."""

    def __init__(self, application: QApplication) -> None:
        self.application = application
        self.current_theme = Theme.DARK

    def apply_theme(self, theme: Theme | str) -> Theme:
        """
        Apply a theme to the complete QApplication.

        Args:
            theme: Theme enum or theme name.

        Returns:
            The theme that was applied.
        """

        try:
            selected_theme = (
                theme if isinstance(theme, Theme) else Theme(str(theme).lower())
            )
        except ValueError:
            selected_theme = Theme.DARK

        if selected_theme == Theme.LIGHT:
            self.application.setStyleSheet(LIGHT_STYLESHEET)
        else:
            self.application.setStyleSheet(DARK_STYLESHEET)

        self.current_theme = selected_theme
        return selected_theme

    def toggle_theme(self) -> Theme:
        """Switch between dark and light themes."""

        new_theme = (
            Theme.LIGHT
            if self.current_theme == Theme.DARK
            else Theme.DARK
        )

        return self.apply_theme(new_theme)