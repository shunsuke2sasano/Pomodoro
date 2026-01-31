"""
Entry point for the Pomodoro timer app.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Ensure settings.json is stored in this directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from settings import Settings
from ui_widget import PomodoroWidget

from PySide6.QtGui import QIcon
from pathlib import Path

def main() -> None:
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

    def on_quit() -> None:
        settings.save()

    app.aboutToQuit.connect(on_quit)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

