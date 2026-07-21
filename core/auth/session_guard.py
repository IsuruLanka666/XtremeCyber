"""
Automatic logout after a period of user inactivity.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QTimer, Signal


class SessionGuard(QObject):
    """Track user activity and emit a signal when the session expires."""

    session_expired = Signal()

    _ACTIVITY_EVENTS = {
        QEvent.Type.KeyPress,
        QEvent.Type.MouseButtonPress,
        QEvent.Type.MouseButtonDblClick,
        QEvent.Type.Wheel,
        QEvent.Type.TouchBegin,
    }

    def __init__(
        self,
        timeout_minutes: int = 30,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self.timeout_minutes = max(1, int(timeout_minutes))

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.session_expired.emit)

    def start(self) -> None:
        """Start or restart inactivity monitoring."""

        self._restart_timer()

    def stop(self) -> None:
        """Stop inactivity monitoring."""

        self.timer.stop()

    def eventFilter(
        self,
        watched: QObject,
        event: QEvent,
    ) -> bool:
        if event.type() in self._ACTIVITY_EVENTS:
            self._restart_timer()

        return super().eventFilter(watched, event)

    def _restart_timer(self) -> None:
        timeout_ms = self.timeout_minutes * 60 * 1000
        self.timer.start(timeout_ms)
