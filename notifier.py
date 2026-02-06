"""
Windows notifications and sounds.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtWidgets import QSystemTrayIcon


_TRAY: "QSystemTrayIcon | None" = None
_TRAY_INITIALIZED = False


def init_tray(icon_path: str | None = None) -> None:
    """Initialize system tray icon (best-effort)."""
    global _TRAY, _TRAY_INITIALIZED
    if _TRAY_INITIALIZED:
        return
    try:
        from PySide6.QtWidgets import QApplication, QSystemTrayIcon
        from PySide6.QtGui import QIcon
    except Exception:
        return
    app = QApplication.instance()
    if app is None:
        return
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return
    try:
        tray = QSystemTrayIcon(app)
        if icon_path:
            tray.setIcon(QIcon(icon_path))
        tray.show()
        _TRAY = tray
        _TRAY_INITIALIZED = True
    except Exception:
        return


def show_notification(title: str, message: str) -> None:
    """Show a tray balloon notification (best-effort)."""
    init_tray()
    tray = _TRAY
    if tray is None:
        return
    try:
        from PySide6.QtWidgets import QSystemTrayIcon
        tray.showMessage(title, message, QSystemTrayIcon.Information, 5000)
    except Exception:
        return


_PLAYERS: dict[str, tuple["QMediaPlayer", "QAudioOutput"]] = {}
_SOUND_FILES = {
    "lion": "assets/sounds/lion.wav",
    "mountain": "assets/sounds/mountain.wav",
    "tombi": "assets/sounds/tombi.wav",
    "cuckoo": "assets/sounds/cuckoo.wav",
}


def play_sound(sound_key: str = "beep", volume: float = 0.9) -> None:
    """Play finish sound by key (best-effort)."""
    rel_path = _SOUND_FILES.get(sound_key)
    if not rel_path:
        return

    path = Path(__file__).resolve().parent / rel_path
    try:
        from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtWidgets import QApplication
    except Exception:
        return

    try:
        if not path.exists():
            QGuiApplication.beep()
            return

        player, audio = _PLAYERS.get(sound_key, (None, None))
        if player is None:
            app = QApplication.instance()
            audio = QAudioOutput(app)
            player = QMediaPlayer(app)
            player.setAudioOutput(audio)
            _PLAYERS[sound_key] = (player, audio)

        audio.setVolume(max(0.0, min(1.0, float(volume))))
         # Always refresh source & restart reliably
        player.setSource(QUrl.fromLocalFile(str(path)))
        player.stop()
        player.setPosition(0)
        player.play()
    except Exception:
        try:
            QGuiApplication.beep()
        except Exception:
            return


def prewarm_sounds() -> None:
    """Preload sound players to reduce first-play latency."""
    try:
        from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
        from PySide6.QtCore import QUrl
        from PySide6.QtWidgets import QApplication
    except Exception:
        return

    app = QApplication.instance()
    if app is None:
        return
    for sound_key, rel_path in _SOUND_FILES.items():
        path = Path(__file__).resolve().parent / rel_path
        if not path.exists():
            continue
        if sound_key in _PLAYERS:
            continue
        try:
            audio = QAudioOutput(app)
            player = QMediaPlayer(app)
            player.setAudioOutput(audio)
            player.setSource(QUrl.fromLocalFile(str(path)))
            _PLAYERS[sound_key] = (player, audio)
        except Exception:
            continue
