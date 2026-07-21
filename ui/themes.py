
"""
XtremeCyber themes
"""

from __future__ import annotations

from PySide6.QtWidgets import QApplication
from core.constants import Theme


DARK_STYLESHEET = """
QWidget {
    background-color: transparent;
    color: #EAFBF2;
    font-family: "Segoe UI";
    font-size: 14px;
}

QMainWindow,
QWidget#applicationRoot,
QFrame#mainArea,
QFrame#pageBackground {
    background-color: #070B0D;
}

QFrame#sidebar {
    background-color: #0B1013;
    border: none;
    border-right: 1px solid #1C2B24;
}

QFrame#topBar {
    background-color: #090E11;
    border: none;
    border-bottom: 1px solid #17231E;
}

QFrame#brandIcon {
    background-color: #353AA6;
    border: 1px solid #545ACC;
    border-radius: 24px;
}

QLabel#brandInitials {
    color: #FFFFFF;
    font-size: 23px;
    font-weight: 900;
}

QLabel#applicationTitle {
    color: #F3FFF8;
    font-size: 20px;
    font-weight: 800;
}

QLabel#applicationSubtitle {
    color: #708579;
    font-size: 11px;
}

QLabel#navigationSectionLabel {
    color: #4C6256;
    font-size: 10px;
    font-weight: 800;
}

QPushButton#navigationButton {
    background-color: transparent;
    color: #94AA9D;
    border: none;
    border-radius: 12px;
    padding: 13px 15px;
    text-align: left;
    font-size: 14px;
    font-weight: 650;
}

QPushButton#navigationButton:hover {
    background-color: #101A15;
    color: #D9FFEA;
}

QPushButton#navigationButton:checked {
    background-color: #0D2518;
    color: #4DFF95;
    border-left: 3px solid #00E676;
}

QLabel#topPageTitle {
    color: #EFFFF6;
    font-size: 21px;
    font-weight: 800;
}

QLabel#topPageSubtitle {
    color: #6D8376;
    font-size: 12px;
}

QLabel#accentHeading {
    color: #3CF28A;
    font-size: 32px;
    font-weight: 900;
}

QLabel#pageSubtitle {
    color: #81968A;
    font-size: 13px;
}

QLabel#sectionTitle {
    color: #EEFFF5;
    font-size: 17px;
    font-weight: 800;
}

QLabel#sectionSubtitle {
    color: #73877C;
    font-size: 12px;
}

QFrame#heroPanel {
    background-color: #0E1518;
    border: 1px solid #1F342A;
    border-radius: 24px;
}

QLabel#heroBadge {
    color: #66FFA6;
    background-color: #0A2A19;
    border: 1px solid #145C33;
    border-radius: 10px;
    padding: 5px 10px;
    font-size: 10px;
    font-weight: 800;
}

QLabel#heroTitle {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 850;
}

QLabel#heroHighlight {
    color: #20E978;
    font-size: 26px;
    font-weight: 900;
}

QLabel#heroDescription {
    color: #92A89B;
    font-size: 13px;
}

QFrame#heroVisual {
    background-color: #0A2316;
    border: 1px solid #126A38;
    border-radius: 22px;
}

QFrame#heroOrb {
    background-color: #353AA6;
    border: 1px solid #545ACC;
    border-radius: 52px;
}

QLabel#heroOrbText {
    color: #FFFFFF;
    font-size: 30px;
    font-weight: 900;
}

QFrame#statCard {
    background-color: #0D1316;
    border: 1px solid #1C2A24;
    border-radius: 18px;
}

QFrame#statCard:hover {
    background-color: #101A15;
    border-color: #1A6D3D;
}

QFrame#statIconBlue,
QFrame#statIconPurple,
QFrame#statIconGreen,
QFrame#statIconOrange {
    background-color: #0B2B1A;
    border: 1px solid #185735;
    border-radius: 13px;
}

QLabel#statIconText {
    color: #47F58E;
    font-size: 15px;
    font-weight: 900;
}

QLabel#cardTitle {
    color: #789087;
    font-size: 12px;
    font-weight: 700;
}

QLabel#cardValue {
    color: #F7FFFA;
    font-size: 28px;
    font-weight: 900;
}

QLabel#cardDescription {
    color: #5F7469;
    font-size: 11px;
}

QFrame#contentCard {
    background-color: #0C1215;
    border: 1px solid #1A2822;
    border-radius: 21px;
}

QFrame#compactInfoCard {
    background-color: #0D1512;
    border: 1px solid #1B3124;
    border-radius: 15px;
}

QPushButton {
    background-color: #111A16;
    color: #D9FCE8;
    border: 1px solid #25372E;
    border-radius: 12px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 700;
}

QPushButton:hover {
    background-color: #16241C;
    border-color: #00E676;
    color: #FFFFFF;
}

QPushButton#primaryButton,
QPushButton#accentButton {
    background-color: #00D96B;
    color: #06110A;
    border: none;
    font-weight: 850;
}

QPushButton#primaryButton:hover,
QPushButton#accentButton:hover {
    background-color: #36F58D;
}

QPushButton#secondaryButton {
    background-color: transparent;
    color: #A8C6B5;
    border: 1px solid #315441;
}

QLineEdit,
QComboBox,
QSpinBox {
    background-color: #0A1012;
    color: #F3FFF8;
    border: 1px solid #22342B;
    border-radius: 11px;
    padding: 10px 12px;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus {
    border: 1px solid #00E676;
}

QTableWidget {
    background-color: #091012;
    alternate-background-color: #0C1416;
    color: #DDF8E8;
    border: none;
    border-radius: 13px;
    gridline-color: #17241E;
    selection-background-color: #103A23;
    selection-color: #FFFFFF;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #17241E;
}

QHeaderView::section {
    background-color: #101816;
    color: #6EF3A6;
    border: none;
    padding: 11px;
    font-size: 11px;
    font-weight: 800;
}

QStatusBar {
    background-color: #090E11;
    color: #65796E;
    border-top: 1px solid #17231E;
}
"""


LIGHT_STYLESHEET = """
QWidget {
    background-color: transparent;
    color: #102118;
    font-family: "Segoe UI";
    font-size: 14px;
}

QMainWindow,
QWidget#applicationRoot,
QFrame#mainArea,
QFrame#pageBackground {
    background-color: #F4F8F5;
}

QFrame#sidebar {
    background-color: #FFFFFF;
    border: none;
    border-right: 1px solid #DCE8E0;
}

QFrame#topBar {
    background-color: #F8FBF9;
    border-bottom: 1px solid #DFEAE3;
}

QFrame#brandIcon {
    background-color: #353AA6;
    border: 1px solid #545ACC;
    border-radius: 24px;
}

QLabel#brandInitials {
    color: #FFFFFF;
    font-size: 23px;
    font-weight: 900;
}

QLabel#applicationTitle {
    color: #102118;
    font-size: 20px;
    font-weight: 800;
}

QLabel#applicationSubtitle,
QLabel#topPageSubtitle,
QLabel#pageSubtitle,
QLabel#sectionSubtitle {
    color: #71847A;
}

QLabel#navigationSectionLabel {
    color: #9AABA1;
    font-size: 10px;
    font-weight: 800;
}

QPushButton#navigationButton {
    background-color: transparent;
    color: #61766A;
    border: none;
    border-radius: 12px;
    padding: 13px 15px;
    text-align: left;
    font-size: 14px;
    font-weight: 650;
}

QPushButton#navigationButton:hover {
    background-color: #ECF8F0;
    color: #0A6A36;
}

QPushButton#navigationButton:checked {
    background-color: #DDF7E7;
    color: #08713A;
    border-left: 3px solid #00C864;
}

QLabel#topPageTitle,
QLabel#sectionTitle {
    color: #102118;
    font-weight: 800;
}

QLabel#topPageTitle { font-size: 21px; }
QLabel#accentHeading { color: #00A853; font-size: 32px; font-weight: 900; }
QLabel#sectionTitle { font-size: 17px; }

QFrame#heroPanel,
QFrame#statCard,
QFrame#contentCard {
    background-color: #FFFFFF;
    border: 1px solid #DBE7DF;
}

QFrame#heroPanel { border-radius: 24px; }
QFrame#statCard { border-radius: 18px; }
QFrame#contentCard { border-radius: 21px; }

QLabel#heroBadge {
    color: #08713A;
    background-color: #E4F8EC;
    border: 1px solid #BFE8CF;
    border-radius: 10px;
    padding: 5px 10px;
    font-size: 10px;
    font-weight: 800;
}

QLabel#heroTitle { color: #102118; font-size: 25px; font-weight: 850; }
QLabel#heroHighlight { color: #00A853; font-size: 26px; font-weight: 900; }
QLabel#heroDescription { color: #6B8074; font-size: 13px; }

QFrame#heroVisual {
    background-color: #E8F9EF;
    border: 1px solid #BEE7CD;
    border-radius: 22px;
}

QFrame#heroOrb {
    background-color: #353AA6;
    border: 1px solid #545ACC;
    border-radius: 52px;
}

QLabel#heroOrbText {
    color: #FFFFFF;
    font-size: 30px;
    font-weight: 900;
}

QFrame#statIconBlue,
QFrame#statIconPurple,
QFrame#statIconGreen,
QFrame#statIconOrange {
    background-color: #E5F8EC;
    border: 1px solid #C5EBD3;
    border-radius: 13px;
}

QLabel#statIconText { color: #00A853; font-size: 15px; font-weight: 900; }
QLabel#cardTitle { color: #71847A; font-size: 12px; font-weight: 700; }
QLabel#cardValue { color: #102118; font-size: 28px; font-weight: 900; }
QLabel#cardDescription { color: #8A9B91; font-size: 11px; }

QFrame#compactInfoCard {
    background-color: #F7FBF8;
    border: 1px solid #DDE9E1;
    border-radius: 15px;
}

QPushButton {
    background-color: #FFFFFF;
    color: #274134;
    border: 1px solid #D6E4DB;
    border-radius: 12px;
    padding: 10px 16px;
    font-weight: 700;
}

QPushButton#primaryButton,
QPushButton#accentButton {
    background-color: #00C864;
    color: #06110A;
    border: none;
    font-weight: 850;
}

QPushButton#secondaryButton {
    background-color: #FFFFFF;
    color: #08713A;
    border: 1px solid #BFDCCB;
}

QTableWidget {
    background-color: #FFFFFF;
    alternate-background-color: #FAFCFB;
    color: #254033;
    border: none;
    border-radius: 13px;
    selection-background-color: #DDF7E7;
}

QHeaderView::section {
    background-color: #F3F8F5;
    color: #0A8F49;
    border: none;
    padding: 11px;
    font-size: 11px;
    font-weight: 800;
}
"""


class ThemeManager:
    def __init__(self, application: QApplication) -> None:
        self.application = application
        self.current_theme = Theme.DARK

    def apply_theme(self, theme: Theme | str) -> Theme:
        try:
            selected = (
                theme if isinstance(theme, Theme)
                else Theme(str(theme).strip().lower())
            )
        except ValueError:
            selected = Theme.DARK

        self.application.setStyleSheet(
            LIGHT_STYLESHEET if selected == Theme.LIGHT else DARK_STYLESHEET
        )
        self.current_theme = selected
        return selected

    def toggle_theme(self) -> Theme:
        return self.apply_theme(
            Theme.LIGHT if self.current_theme == Theme.DARK else Theme.DARK
        )
