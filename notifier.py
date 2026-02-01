"""
Windows notifications and sounds.
"""

from pathlib import Path


def show_notification(title: str, message: str) -> None:
    """Show a Windows toast notification (best-effort)."""
    try:
        import subprocess

        ps_code = f'''
$notification = [Windows.UI.Notifications.ToastNotificationManager,
    Windows.UI.Notifications,ContentType=WindowsRuntime]
try {{
    $app = "Microsoft.WindowsTerminal"
    $toaster = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app)
    $xmlString = @"
<toast version="2">
  <visual>
    <binding template="ToastBasic">
      <text id="1">{_escape_xml(title)}</text>
      <text id="2">{_escape_xml(message)}</text>
    </binding>
  </visual>
</toast>
"@
    $xmlDoc = [Windows.Data.Xml.Dom.XmlDocument]::new()
    $xmlDoc.LoadXml($xmlString)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xmlDoc)
    $toaster.Show($toast)
}} catch {{
    # Fail silently.
}}
'''
        subprocess.Popen(
            ["powershell", "-WindowStyle", "Hidden", "-NoProfile", "-Command", ps_code],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


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


def _escape_xml(s: str) -> str:
    """Escape XML special characters."""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&apos;")
    )
