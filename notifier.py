"""
Windows notifications and sounds.
"""

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


def play_sound(sound_type: str = "default") -> None:
    """Play a simple system beep sound (best-effort)."""

    def _play() -> None:
        try:
            import winsound
            if sound_type == "finish":
                for _ in range(3):
                    winsound.Beep(880, 200)
                    winsound.Beep(1100, 150)
            else:
                winsound.Beep(660, 300)
        except ImportError:
            pass
        except Exception:
            pass

    t = threading.Thread(target=_play, daemon=True)
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
