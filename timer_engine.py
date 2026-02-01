"""
Timer engine: state machine and countdown logic.
UI should communicate via signals only.
"""

from PySide6.QtCore import QObject, QTimer, Signal

from constants import (
    MODE_WORK,
    MODE_SHORT,
    MODE_LONG,
    SETS_BEFORE_LONG,
    MAX_DIAL_MIN,
)
from settings import Settings


class TimerState:
    """Timer state."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


class TimerEngine(QObject):
    """
    Signals:
      tick(int): remaining seconds changed
      finished(str): mode finished
      state_changed(str): state changed
      mode_changed(str): mode changed
    """
    tick = Signal(int)
    finished = Signal(str)
    state_changed = Signal(str)
    mode_changed = Signal(str)

    def __init__(self, settings: Settings, parent: QObject | None = None):
        super().__init__(parent)
        self._settings = settings

        self._mode: str = settings.last_mode
        self._state: str = TimerState.IDLE
        self._total_seconds: int = 0
        self._remaining: int = 0
        self._work_count: int = 0
        self._manual_duration: bool = True

        self._qtimer = QTimer(self)
        self._qtimer.setInterval(1000)
        self._qtimer.timeout.connect(self._on_tick)

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def state(self) -> str:
        return self._state

    @property
    def remaining(self) -> int:
        return self._remaining

    @property
    def total(self) -> int:
        return self._total_seconds

    @property
    def work_count(self) -> int:
        return self._work_count

    def start_or_pause(self) -> None:
        """Start/Pause toggle."""
        if self._state == TimerState.RUNNING:
            self._pause()
        elif self._remaining > 0:
            self._start()

    def set_duration(self, seconds: int) -> None:
        """Set duration from dial (IDLE/PAUSED only)."""
        if self._state not in (TimerState.IDLE, TimerState.PAUSED):
            return
        max_seconds = MAX_DIAL_MIN * 60
        clamped = max(0, min(max_seconds, int(seconds)))
        self._manual_duration = True
        self._total_seconds = clamped
        self._remaining = clamped
        self.tick.emit(self._remaining)
        self.state_changed.emit(self._state)

    def reset(self) -> None:
        """Reset to 00:00."""
        self._qtimer.stop()
        self._state = TimerState.IDLE
        self._manual_duration = True
        self._total_seconds = 0
        self._remaining = 0
        self.tick.emit(self._remaining)
        self.state_changed.emit(self._state)

    def set_mode(self, mode: str) -> None:
        """Switch mode and reset to its preset."""
        self._qtimer.stop()
        self._state = TimerState.IDLE
        self._mode = mode
        self._settings.last_mode = mode
        self._manual_duration = False
        self._load_mode_duration()
        self.mode_changed.emit(self._mode)
        self.tick.emit(self._remaining)
        self.state_changed.emit(self._state)

    def _load_mode_duration(self) -> None:
        """Load duration from preset for current mode."""
        minutes_map = {
            MODE_WORK: self._settings.preset_work,
            MODE_SHORT: self._settings.preset_short,
            MODE_LONG: self._settings.preset_long,
        }
        mins = minutes_map.get(self._mode, 25)
        self._total_seconds = mins * 60
        self._remaining = self._total_seconds

    def _start(self) -> None:
        if self._remaining <= 0:
            return
        self._state = TimerState.RUNNING
        self._qtimer.start()
        self.state_changed.emit(self._state)

    def _pause(self) -> None:
        self._qtimer.stop()
        self._state = TimerState.PAUSED
        self.state_changed.emit(self._state)

    def _on_tick(self) -> None:
        """Called every second."""
        self._remaining -= 1
        if self._remaining < 0:
            self._remaining = 0
        self.tick.emit(self._remaining)

        if self._remaining <= 0:
            self._qtimer.stop()
            self._state = TimerState.IDLE
            self.state_changed.emit(self._state)
            self.finished.emit(self._mode)
            if not self._manual_duration:
                self._advance_mode()

    def _advance_mode(self) -> None:
        """Mode progression: Work -> Short/Long -> Work."""
        if self._mode == MODE_WORK:
            self._work_count += 1
            if self._work_count >= SETS_BEFORE_LONG:
                self._mode = MODE_LONG
                self._work_count = 0
            else:
                self._mode = MODE_SHORT
        else:
            self._mode = MODE_WORK

        self._settings.last_mode = self._mode
        self._load_mode_duration()
        self.mode_changed.emit(self._mode)
        self.tick.emit(self._remaining)
