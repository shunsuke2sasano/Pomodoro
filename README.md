# Pomodoro Timer (Dial Widget)

## Files
- `main.py` - app entry point
- `constants.py` - layout, fonts, colors, themes
- `settings.py` - settings.json load/save
- `timer_engine.py` - countdown state machine
- `ui_widget.py` - widget rendering and input handling
- `notifier.py` - Windows notifications and sound

## Requirements
- Python 3.11+
- PySide6

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install PySide6
```

## Run
```powershell
python main.py
```

## Controls
- Left click (no drag): Start / Pause / Resume
- Drag inside dial: set minutes (0–60)
- Drag outside dial: move window
- Right click: context menu (Reset / Mode / Presets / Theme / Always on Top / Sound / Quit)

## Settings (settings.json)
Stored automatically on exit:
- window position
- always-on-top
- sound on/off
- preset minutes
- last mode
- theme name
