"""
PySide6 application bootstrap for XtremeCyber.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox

from config import APP_NAME, THEME, VERSION
from core.constants import Theme
from core.database.database import database_manager
from core.database.repository import SettingsRepository
from core.helpers import ensure_directories
from core.logger import configure_logging, get_logger
from ui.main_window import MainWindow
from ui.splash import SplashScreen
from ui.themes import ThemeManager


logger = get_logger(__name__)


class XtremeCyberApplication:
    """Coordinate startup and lifetime of the Qt application."""

    def __init__(self) -> None:
        self.qt_application = QApplication(sys.argv)

        self.qt_application.setApplicationName(APP_NAME)
        self.qt_application.setApplicationVersion(VERSION)
        self.qt_application.setOrganizationName("XtremeCyber")

        self.qt_application.setFont(QFont("Segoe UI", 10))

        self.theme_manager = ThemeManager(self.qt_application)
        self.settings_repository = SettingsRepository()

        self.splash_screen: SplashScreen | None = None
        self.main_window: MainWindow | None = None

        self._startup_stage = 0

    def run(self) -> int:
        """Initialize and execute the Qt event loop."""

        try:
            self._prepare_application()
            self._show_splash_screen()

            return self.qt_application.exec()

        except Exception as exc:
            logger.exception("Application startup failed.")

            QMessageBox.critical(
                None,
                "XtremeCyber Startup Error",
                (
                    "XtremeCyber could not start successfully.\n\n"
                    f"Details: {exc}"
                ),
            )

            return 1

    def _prepare_application(self) -> None:
        ensure_directories()
        configure_logging()
        database_manager.initialize()

        stored_theme = self.settings_repository.get(
            "theme",
            THEME,
        )

        self.theme_manager.apply_theme(stored_theme or Theme.DARK.value)

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
            (75, "Preparing user interface..."),
            (90, "Loading dashboard..."),
            (100, "XtremeCyber is ready."),
        ]

        if self._startup_stage < len(startup_stages):
            progress, message = startup_stages[self._startup_stage]

            self.splash_screen.set_progress(progress, message)
            self._startup_stage += 1

            QTimer.singleShot(280, self._advance_startup)
            return

        self._open_main_window()

    def _open_main_window(self) -> None:
        self.main_window = MainWindow()

        self.main_window.theme_change_requested.connect(
            self._toggle_theme
        )

        self.main_window.set_active_theme(
            self.theme_manager.current_theme
        )

        self.main_window.show()

        if self.splash_screen is not None:
            self.splash_screen.close()
            self.splash_screen.deleteLater()
            self.splash_screen = None

        logger.info("Main application window displayed.")

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
    """Create and run the XtremeCyber GUI application."""

    application = XtremeCyberApplication()
    return application.run()