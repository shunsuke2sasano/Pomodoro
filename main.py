"""
Entry point for the Pomodoro timer app.
"""

import sys
from pathlib import Path
import traceback

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Ensure settings.json is stored in this directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from settings import Settings
from ui_widget import PomodoroWidget
from notifier import prewarm_sounds, init_tray

from PySide6.QtGui import QIcon

def main() -> None:
    try:
        # Enable high-DPI scaling (Qt6 default, but explicit is safe).
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

        app = QApplication.instance() or QApplication(sys.argv)
        app.setApplicationName("PomodoroTimer")
        app.setOrganizationName("PomoApp")

        icon_path = Path(__file__).resolve().parent / "assets" / "icon.ico"
        app.setWindowIcon(QIcon(str(icon_path)))
        
        settings = Settings()

        widget = PomodoroWidget(settings)
        widget.setWindowIcon(QIcon(str(icon_path)))
        widget.show()
        init_tray(str(icon_path))
        prewarm_sounds()

        def on_quit() -> None:
            settings.save()

        app.aboutToQuit.connect(on_quit)
        sys.exit(app.exec())
    except Exception:
        crash_path = Path(__file__).resolve().parent / "crash.log"
        try:
            crash_path.write_text(traceback.format_exc(), encoding="utf-8")
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
