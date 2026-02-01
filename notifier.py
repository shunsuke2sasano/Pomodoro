"""
Windows notifications and sounds.
"""

from pathlib import Path
import threading


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


_SOUND_EFFECTS: dict[str, object] = {}
_SOUND_FILES = {
    "chime": "sounds/chime.wav",
    "premium": "sounds/premium.wav",
}


def play_sound(sound_key: str = "beep") -> None:
    """Play finish sound by key (best-effort)."""

    def _beep() -> None:
        try:
            import winsound
            winsound.Beep(880, 200)
            winsound.Beep(1100, 150)
        except Exception:
            pass

    if sound_key == "beep":
        t = threading.Thread(target=_beep, daemon=True)
        t.start()
        return

    rel_path = _SOUND_FILES.get(sound_key)
    if not rel_path:
        t = threading.Thread(target=_beep, daemon=True)
        t.start()
        return

    path = Path(__file__).resolve().parent / rel_path
    if not path.exists():
        t = threading.Thread(target=_beep, daemon=True)
        t.start()
        return

    try:
        from PySide6.QtMultimedia import QSoundEffect
        from PySide6.QtCore import QUrl
    except Exception:
        t = threading.Thread(target=_beep, daemon=True)
        t.start()
        return

    effect = _SOUND_EFFECTS.get(sound_key)
    if effect is None:
        effect = QSoundEffect()
        effect.setSource(QUrl.fromLocalFile(str(path)))
        effect.setLoopCount(1)
        effect.setVolume(0.9)
        _SOUND_EFFECTS[sound_key] = effect

    try:
        effect.play()
    except Exception:
        t = threading.Thread(target=_beep, daemon=True)
        t.start()


def _escape_xml(s: str) -> str:
    """Escape XML special characters."""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&apos;")
    )
