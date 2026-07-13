"""
Modern dark and light themes for the XtremeCyber desktop application.
"""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from core.constants import Theme


DARK_STYLESHEET = """
QWidget {
    background-color: transparent;
    color: #F7F8FF;
    font-family: "Segoe UI";
    font-size: 14px;
}

QMainWindow,
QWidget#applicationRoot,
QFrame#mainArea,
QFrame#pageBackground {
    background-color: #090D24;
}

QFrame#sidebar {
    background-color: #101632;
    border: none;
    border-right: 1px solid #202848;
}

QFrame#topBar {
    background-color: #090D24;
    border: none;
}

QFrame#brandIcon {
    background-color: #5265FF;
    border: none;
    border-radius: 16px;
}

QLabel#brandInitials {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 800;
}

QLabel#applicationTitle {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 800;
}

QLabel#applicationSubtitle {
    color: #929BBC;
    font-size: 11px;
}

QLabel#navigationSectionLabel {
    color: #626D94;
    font-size: 10px;
    font-weight: 700;
}

QPushButton#navigationButton {
    background-color: transparent;
    color: #A8B0D0;
    border: none;
    border-radius: 14px;
    padding: 13px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
}

QPushButton#navigationButton:hover {
    background-color: #171F42;
    color: #FFFFFF;
}

QPushButton#navigationButton:checked {
    background-color: #5265FF;
    color: #FFFFFF;
}

QLabel#topPageTitle {
    color: #FFFFFF;
    font-size: 21px;
    font-weight: 800;
}

QLabel#topPageSubtitle {
    color: #8791B5;
    font-size: 12px;
}

QLabel#pageTitle {
    color: #FFFFFF;
    font-size: 30px;
    font-weight: 800;
}

QLabel#pageSubtitle {
    color: #929BBC;
    font-size: 13px;
}

QLabel#sectionTitle {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 750;
}

QLabel#sectionSubtitle {
    color: #8490B5;
    font-size: 12px;
}

QFrame#heroPanel {
    background-color: #5265FF;
    border: none;
    border-radius: 25px;
}

QLabel#heroBadge {
    color: #DDE2FF;
    background-color: #6677FF;
    border-radius: 10px;
    padding: 5px 10px;
    font-size: 10px;
    font-weight: 700;
}

QLabel#heroTitle {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 800;
}

QLabel#heroDescription {
    color: #E1E5FF;
    font-size: 13px;
}

QFrame#heroDecorationOne {
    background-color: #7080FF;
    border-radius: 52px;
}

QFrame#heroDecorationTwo {
    background-color: #3C4FE7;
    border-radius: 35px;
}

QFrame#statCard {
    background-color: #151C3A;
    border: 1px solid #252E53;
    border-radius: 20px;
}

QFrame#statCard:hover {
    border: 1px solid #5265FF;
    background-color: #182041;
}

QFrame#statIconBlue { background-color: #263A79; border-radius: 14px; }
QFrame#statIconPurple { background-color: #3C2C72; border-radius: 14px; }
QFrame#statIconGreen { background-color: #164F50; border-radius: 14px; }
QFrame#statIconOrange { background-color: #5D3A29; border-radius: 14px; }

QLabel#statIconText {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 800;
}

QLabel#cardTitle {
    color: #8E98BA;
    font-size: 12px;
    font-weight: 650;
}

QLabel#cardValue {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: 800;
}

QLabel#cardDescription {
    color: #6F7A9E;
    font-size: 11px;
}

QFrame#contentCard {
    background-color: #151C3A;
    border: 1px solid #252E53;
    border-radius: 22px;
}

QFrame#compactInfoCard {
    background-color: #1A2243;
    border: 1px solid #2C365E;
    border-radius: 16px;
}

QPushButton {
    background-color: #1A2242;
    color: #E9ECFF;
    border: 1px solid #303A61;
    border-radius: 13px;
    padding: 10px 17px;
    font-size: 13px;
    font-weight: 650;
}

QPushButton:hover {
    background-color: #222C51;
    border-color: #5265FF;
}

QPushButton#primaryButton {
    background-color: #FFFFFF;
    color: #3547D3;
    border: none;
    font-weight: 750;
}

QPushButton#accentButton {
    background-color: #5265FF;
    color: #FFFFFF;
    border: none;
    font-weight: 750;
}

QPushButton#secondaryButton {
    background-color: #1B2447;
    color: #DDE2FF;
    border: 1px solid #303B68;
}

QLineEdit,
QComboBox,
QSpinBox {
    background-color: #101733;
    color: #F5F6FF;
    border: 1px solid #2A345B;
    border-radius: 12px;
    padding: 10px 12px;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus {
    border: 1px solid #6677FF;
}

QTableWidget {
    background-color: #111831;
    alternate-background-color: #141C39;
    color: #DDE2F8;
    border: none;
    border-radius: 14px;
    gridline-color: #252E50;
    selection-background-color: #3445A6;
    selection-color: #FFFFFF;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #222B4D;
}

QHeaderView::section {
    background-color: #1A2242;
    color: #9DA7C8;
    border: none;
    padding: 11px;
    font-size: 11px;
    font-weight: 700;
}

QTableCornerButton::section {
    background-color: #1A2242;
    border: none;
}

QProgressBar {
    background-color: #182041;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    text-align: center;
    min-height: 16px;
}

QProgressBar::chunk {
    background-color: #5265FF;
    border-radius: 8px;
}

QStatusBar {
    background-color: #101632;
    color: #7F89AA;
    border-top: 1px solid #202848;
}

QScrollBar:vertical {
    background-color: transparent;
    width: 10px;
    margin: 3px;
}

QScrollBar::handle:vertical {
    background-color: #303A60;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5265FF;
}
"""


LIGHT_STYLESHEET = """
QWidget {
    background-color: transparent;
    color: #17203F;
    font-family: "Segoe UI";
    font-size: 14px;
}

QMainWindow,
QWidget#applicationRoot,
QFrame#mainArea,
QFrame#pageBackground {
    background-color: #F1F4FF;
}

QFrame#sidebar {
    background-color: #FFFFFF;
    border: none;
    border-right: 1px solid #E2E6F4;
}

QFrame#topBar {
    background-color: #F1F4FF;
    border: none;
}

QFrame#brandIcon {
    background-color: #5265FF;
    border-radius: 16px;
}

QLabel#brandInitials {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 800;
}

QLabel#applicationTitle {
    color: #17203F;
    font-size: 20px;
    font-weight: 800;
}

QLabel#applicationSubtitle {
    color: #7F89A8;
    font-size: 11px;
}

QLabel#navigationSectionLabel {
    color: #A0A8BF;
    font-size: 10px;
    font-weight: 700;
}

QPushButton#navigationButton {
    background-color: transparent;
    color: #737D9F;
    border: none;
    border-radius: 14px;
    padding: 13px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
}

QPushButton#navigationButton:hover {
    background-color: #EEF0FF;
    color: #394ACB;
}

QPushButton#navigationButton:checked {
    background-color: #5265FF;
    color: #FFFFFF;
}

QLabel#topPageTitle,
QLabel#sectionTitle {
    color: #17203F;
    font-weight: 800;
}

QLabel#topPageTitle { font-size: 21px; }
QLabel#topPageSubtitle,
QLabel#pageSubtitle,
QLabel#sectionSubtitle { color: #7781A0; }

QLabel#topPageSubtitle { font-size: 12px; }
QLabel#pageTitle { color: #17203F; font-size: 30px; font-weight: 800; }
QLabel#pageSubtitle { font-size: 13px; }
QLabel#sectionTitle { font-size: 17px; }
QLabel#sectionSubtitle { font-size: 12px; }

QFrame#heroPanel {
    background-color: #5265FF;
    border-radius: 25px;
}

QLabel#heroBadge {
    color: #FFFFFF;
    background-color: #6878FF;
    border-radius: 10px;
    padding: 5px 10px;
    font-size: 10px;
    font-weight: 700;
}

QLabel#heroTitle { color: #FFFFFF; font-size: 25px; font-weight: 800; }
QLabel#heroDescription { color: #E6E9FF; font-size: 13px; }
QFrame#heroDecorationOne { background-color: #7181FF; border-radius: 52px; }
QFrame#heroDecorationTwo { background-color: #3F52DE; border-radius: 35px; }

QFrame#statCard,
QFrame#contentCard {
    background-color: #FFFFFF;
    border: 1px solid #E1E5F2;
}

QFrame#statCard { border-radius: 20px; }
QFrame#statCard:hover { border-color: #5265FF; }
QFrame#contentCard { border-radius: 22px; }

QFrame#compactInfoCard {
    background-color: #F7F8FF;
    border: 1px solid #E3E6F3;
    border-radius: 16px;
}

QFrame#statIconBlue { background-color: #E2E7FF; border-radius: 14px; }
QFrame#statIconPurple { background-color: #EFE5FF; border-radius: 14px; }
QFrame#statIconGreen { background-color: #DDF5EC; border-radius: 14px; }
QFrame#statIconOrange { background-color: #FFE9DD; border-radius: 14px; }

QLabel#statIconText { color: #3D4ED6; font-size: 16px; font-weight: 800; }
QLabel#cardTitle { color: #7B85A3; font-size: 12px; font-weight: 650; }
QLabel#cardValue { color: #17203F; font-size: 28px; font-weight: 800; }
QLabel#cardDescription { color: #9AA2BA; font-size: 11px; }

QPushButton {
    background-color: #FFFFFF;
    color: #34405F;
    border: 1px solid #DDE1EE;
    border-radius: 13px;
    padding: 10px 17px;
    font-weight: 650;
}

QPushButton:hover {
    background-color: #F3F4FF;
    border-color: #5265FF;
}

QPushButton#primaryButton {
    background-color: #FFFFFF;
    color: #3547D3;
    border: none;
}

QPushButton#accentButton {
    background-color: #5265FF;
    color: #FFFFFF;
    border: none;
}

QPushButton#secondaryButton {
    background-color: #FFFFFF;
    color: #5265FF;
    border: 1px solid #D8DDF2;
}

QLineEdit,
QComboBox,
QSpinBox {
    background-color: #FFFFFF;
    color: #17203F;
    border: 1px solid #DDE1EF;
    border-radius: 12px;
    padding: 10px 12px;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus {
    border: 1px solid #5265FF;
}

QTableWidget {
    background-color: #FFFFFF;
    alternate-background-color: #FAFBFF;
    color: #303A58;
    border: none;
    border-radius: 14px;
    gridline-color: #E8EBF4;
    selection-background-color: #E0E5FF;
    selection-color: #273899;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #ECEEF6;
}

QHeaderView::section {
    background-color: #F4F6FC;
    color: #78819D;
    border: none;
    padding: 11px;
    font-size: 11px;
    font-weight: 700;
}

QProgressBar {
    background-color: #E6E9F5;
    color: #17203F;
    border: none;
    border-radius: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #5265FF;
    border-radius: 8px;
}

QStatusBar {
    background-color: #FFFFFF;
    color: #8790AA;
    border-top: 1px solid #E2E6F2;
}
"""


class ThemeManager:
    """Apply and track the current application theme."""

    def __init__(self, application: QApplication) -> None:
        self.application = application
        self.current_theme = Theme.DARK

    def apply_theme(self, theme: Theme | str) -> Theme:
        try:
            selected_theme = (
                theme
                if isinstance(theme, Theme)
                else Theme(str(theme).strip().lower())
            )
        except ValueError:
            selected_theme = Theme.DARK

        self.application.setStyleSheet(
            LIGHT_STYLESHEET
            if selected_theme == Theme.LIGHT
            else DARK_STYLESHEET
        )
        self.current_theme = selected_theme
        return selected_theme

    def toggle_theme(self) -> Theme:
        return self.apply_theme(
            Theme.LIGHT
            if self.current_theme == Theme.DARK
            else Theme.DARK
        )
