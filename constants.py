"""
Shared constants for the app.
All layout, font, and color settings are centralized here.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

# Window
WINDOW_WIDTH = 260
WINDOW_HEIGHT = 260
WINDOW_RADIUS = 24  # corner radius (px)
SHADOW_OFFSET = 4
SHADOW_BLUR = 12

# Dial layout
DISC_MARGIN = 18
TICK_LENGTH_MAJOR = 8
TICK_LENGTH_MINOR = 4
TICK_WIDTH_MAJOR = 2
TICK_WIDTH_MINOR = 1

MAX_DIAL_MIN = 60

# Palette (QColor)
C_BG_OUTER = QColor(28, 30, 34)
C_BG_DISC = QColor(38, 41, 46)
C_BG_INNER = QColor(32, 34, 38)

C_ARC_WORK = QColor(229, 75, 75)
C_ARC_SHORT = QColor(60, 180, 140)
C_ARC_LONG = QColor(70, 145, 220)

C_TICK_MAJOR = QColor(90, 95, 105)
C_TICK_MINOR = QColor(55, 58, 64)

C_TEXT_TIME = QColor(240, 240, 245)
C_TEXT_MODE = QColor(120, 125, 135)
C_TEXT_SET = QColor(90, 95, 105)

C_SHADOW = QColor(0, 0, 0, 80)

# Fonts
FONT_FAMILY = "Segoe UI"
FONT_SIZE_TIME = 30
FONT_SIZE_MODE = 11
FONT_SIZE_SET = 9

# Pomodoro defaults (minutes)
DEFAULT_WORK_MIN = 25
DEFAULT_SHORT_MIN = 5
DEFAULT_LONG_MIN = 15
SETS_BEFORE_LONG = 4

# Mode
MODE_WORK = "work"
MODE_SHORT = "short"
MODE_LONG = "long"

MODE_LABELS = {
    MODE_WORK: "FOCUS",
    MODE_SHORT: "SHORT BREAK",
    MODE_LONG: "LONG BREAK",
}

MODE_COLORS = {
    MODE_WORK: C_ARC_WORK,
    MODE_SHORT: C_ARC_SHORT,
    MODE_LONG: C_ARC_LONG,
}

# Themes
DEFAULT_THEME = "midnight_gold"

THEMES = {
    "midnight_gold": {
        "label": "Midnight Gold",
        "bg_outer": QColor(15, 52, 67),  # #0F3443
        "bg_disc": QColor(23, 58, 70),
        "bg_inner": QColor(11, 40, 50),
        "arc": QColor(180, 154, 82),  # #B49A52
        "tick_major": QColor(255, 255, 255),
        "tick_minor": QColor(220, 220, 220),
        "text_time": QColor(255, 255, 255),
        "text_mode": QColor(255, 255, 255),
        "text_set": QColor(230, 211, 154),  # #E6D39A
        "hand": QColor(230, 211, 154),
        "shadow": QColor(0, 0, 0, 80),
    },
    "dark": {
        "label": "Dark",
        "bg_outer": C_BG_OUTER,
        "bg_disc": C_BG_DISC,
        "bg_inner": C_BG_INNER,
        "arc": C_ARC_WORK,
        "tick_major": C_TICK_MAJOR,
        "tick_minor": C_TICK_MINOR,
        "text_time": C_TEXT_TIME,
        "text_mode": C_TEXT_MODE,
        "text_set": C_TEXT_SET,
        "hand": QColor(240, 240, 245),
        "shadow": C_SHADOW,
    },
    "light": {
        "label": "Light",
        "bg_outer": QColor(240, 242, 246),
        "bg_disc": QColor(225, 228, 234),
        "bg_inner": QColor(250, 250, 252),
        "arc": QColor(96, 120, 160),
        "tick_major": QColor(80, 85, 95),
        "tick_minor": QColor(130, 135, 145),
        "text_time": QColor(40, 42, 46),
        "text_mode": QColor(70, 75, 85),
        "text_set": QColor(90, 95, 105),
        "hand": QColor(40, 42, 46),
        "shadow": QColor(0, 0, 0, 50),
    },
}
