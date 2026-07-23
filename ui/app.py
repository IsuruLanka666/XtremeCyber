"""
XtremeCyber application bootstrap with authentication.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox
from requests import Session

from config import SESSION_TIMEOUT_MINUTES
from config import (
    APP_NAME,
    SESSION_TIMEOUT_MINUTES,
    THEME,
    VERSION,
)
from core.auth.session_guard import SessionGuard
from core.constants import Theme
from core.scanning.persistence import ScanRunRepository
from core.database.database import database_manager
from core.database.repository import SettingsRepository
from core.helpers import ensure_directories
from core.logger import configure_logging, get_logger
from core.vulnerability.persistence import (VulnerabilityRepository,)
from core.vulnerability.intelligence_persistence import (
    VulnerabilityIntelligenceRepository,
)
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from ui.splash import SplashScreen
from ui.themes import ThemeManager


logger = get_logger(__name__)


class XtremeCyberApplication:
    """Coordinate startup, login, logout, and application lifetime."""

    def __init__(self) -> None:
        self.qt_application = QApplication(sys.argv)
        self.qt_application.setApplicationName(APP_NAME)
        self.qt_application.setApplicationVersion(VERSION)
        self.qt_application.setOrganizationName("XtremeCyber")
        self.qt_application.setFont(QFont("Segoe UI", 10))

        self.theme_manager = ThemeManager(self.qt_application)
        self.settings_repository = SettingsRepository()

        self.session_guard = SessionGuard(
        timeout_minutes=SESSION_TIMEOUT_MINUTES,
        parent=self.qt_application,
        )

        self.session_guard.session_expired.connect(
        self._handle_session_expired
        )

        self.qt_application.installEventFilter(
        self.session_guard
        )

        self.splash_screen: SplashScreen | None = None
        self.login_window: LoginWindow | None = None
        self.main_window: MainWindow | None = None

        self._startup_stage = 0

    def run(self) -> int:
        try:
            self._prepare_application()
            self._show_splash_screen()
            return self.qt_application.exec()
        except Exception as exc:
            logger.exception("Application startup failed.")
            QMessageBox.critical(
                None,
                "XtremeCyber Startup Error",
                f"XtremeCyber could not start successfully.\n\nDetails: {exc}",
            )
            return 1

    def _prepare_application(self) -> None:
        ensure_directories()
        configure_logging()
        database_manager.initialize()

        scan_history_repository = ScanRunRepository()
        VulnerabilityRepository()
        VulnerabilityIntelligenceRepository()

        recovered_scans = (
            scan_history_repository.recover_interrupted_scans()
        )

        if recovered_scans:
            logger.warning(
                "Marked %s previous scan(s) as interrupted.",
                recovered_scans,
        )

        stored_theme = self.settings_repository.get("theme", THEME)
        self.theme_manager.apply_theme(
            stored_theme or Theme.DARK.value
        )

        logger.info("Qt application prepared successfully.")

    def _show_splash_screen(self) -> None:
        self.splash_screen = SplashScreen()
        self.splash_screen.show()
        QTimer.singleShot(250, self._advance_startup)

    def _advance_startup(self) -> None:
        if self.splash_screen is None:
            return

        startup_stages = [
            (15, "Loading configuration..."),
            (35, "Connecting to database..."),
            (55, "Loading theme resources..."),
            (75, "Preparing authentication..."),
            (90, "Loading workspace..."),
            (100, "XtremeCyber is ready."),
        ]

        if self._startup_stage < len(startup_stages):
            progress, message = startup_stages[self._startup_stage]
            self.splash_screen.set_progress(progress, message)
            self._startup_stage += 1
            QTimer.singleShot(280, self._advance_startup)
            return

        self._open_login_window()

    def _open_login_window(self) -> None:
        self.login_window = LoginWindow()
        self.login_window.login_succeeded.connect(
            self._open_main_window
        )
        self.login_window.show()

        if self.splash_screen is not None:
            self.splash_screen.close()
            self.splash_screen.deleteLater()
            self.splash_screen = None

        logger.info("Login window displayed.")

    def _open_main_window(self, session) -> None:
        self.main_window = MainWindow(session=session)
        self.main_window.theme_change_requested.connect(
            self._toggle_theme
        )
        self.main_window.logout_requested.connect(
            self._handle_logout
        )
        self.main_window.set_active_theme(
            self.theme_manager.current_theme
        )
        self.main_window.show()

        self.session_guard.start()

        if self.login_window is not None:
            self.login_window.close()
            self.login_window.deleteLater()
            self.login_window = None

        logger.info(
            "Main window displayed for user %s.",
            session.username,
        )

    def _handle_logout(self) -> None:
        self.session_guard.stop()
        
        if self.main_window is not None:
            self.main_window.close()
            self.main_window.deleteLater()
            self.main_window = None

        self._open_login_window()
        logger.info("User logged out.")

    def _handle_session_expired(self) -> None:
        """Sign out the user after the inactivity timeout."""

        QMessageBox.information(
            self.main_window,
            "Session Expired",
            (
            "Your XtremeCyber session expired because no activity "
            "was detected. Please sign in again."
            ),
        )

        logger.info(
            "User session expired because of inactivity."
        )

        self._handle_logout()

    def _toggle_theme(self) -> None:
        selected_theme = self.theme_manager.toggle_theme()

        self.settings_repository.set(
            "theme",
            selected_theme.value,
        )

        if self.main_window is not None:
            self.main_window.set_active_theme(selected_theme)

        logger.info(
            "Application theme changed to %s.",
            selected_theme.value,
        )


def run_application() -> int:
    application = XtremeCyberApplication()
    return application.run()
