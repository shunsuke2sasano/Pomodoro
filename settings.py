"""
settings.py - load/save settings.json in the app directory.
"""

import json
from pathlib import Path

from constants import (
    DEFAULT_WORK_MIN,
    DEFAULT_SHORT_MIN,
    DEFAULT_LONG_MIN,
    DEFAULT_THEME,
    MODE_WORK,
)

_BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = _BASE_DIR / "settings.json"

_DEFAULTS = {
    "window_x": 100,
    "window_y": 100,
    "always_on_top": True,
    "sound_on": True,
    "bg_opacity": 210,
    "finish_sound": "cuckoo",
    "focus_finish_sound": "",
    "break_finish_sound": "",
    "sound_volume": 0.7,
    "preset_work": DEFAULT_WORK_MIN,
    "preset_short": DEFAULT_SHORT_MIN,
    "preset_long": DEFAULT_LONG_MIN,
    "last_mode": MODE_WORK,
    "theme_name": DEFAULT_THEME,
}


class Settings:
    """Simple settings wrapper."""

    def __init__(self):
        self._data: dict = {}
        self.load()

    def load(self) -> None:
        """Load settings.json if available."""
        self._data = dict(_DEFAULTS)
        if SETTINGS_PATH.exists():
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for key in _DEFAULTS:
                    if key in saved:
                        self._data[key] = saved[key]
            except (json.JSONDecodeError, OSError):
                pass

    def save(self) -> None:
        """Persist settings to settings.json."""
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def get(self, key: str):
        return self._data.get(key, _DEFAULTS.get(key))

    def set(self, key: str, value) -> None:
        self._data[key] = value

    @property
    def window_x(self) -> int:
        return int(self.get("window_x"))

    @window_x.setter
    def window_x(self, v: int):
        self.set("window_x", v)

    @property
    def window_y(self) -> int:
        return int(self.get("window_y"))

    @window_y.setter
    def window_y(self, v: int):
        self.set("window_y", v)

    @property
    def always_on_top(self) -> bool:
        return bool(self.get("always_on_top"))

    @always_on_top.setter
    def always_on_top(self, v: bool):
        self.set("always_on_top", v)

    @property
    def sound_on(self) -> bool:
        return bool(self.get("sound_on"))

    @sound_on.setter
    def sound_on(self, v: bool):
        self.set("sound_on", v)

    @property
    def bg_opacity(self) -> int:
        return int(self.get("bg_opacity"))

    @bg_opacity.setter
    def bg_opacity(self, v: int):
        self.set("bg_opacity", max(0, min(255, int(v))))

    @property
    def finish_sound(self) -> str:
        return str(self.get("finish_sound"))

    @finish_sound.setter
    def finish_sound(self, v: str):
        self.set("finish_sound", v)
    @property
    def focus_finish_sound(self) -> str:
        v = self.get("focus_finish_sound")
        if isinstance(v, str) and v:
            return v
        # backward compatible fallback
        return str(self.get("finish_sound") or "cuckoo")

    @focus_finish_sound.setter
    def focus_finish_sound(self, v: str) -> None:
        self.set("focus_finish_sound", v)

    @property
    def break_finish_sound(self) -> str:
        v = self.get("break_finish_sound")
        if isinstance(v, str) and v:
            return v
        # backward compatible fallback
        return str(self.get("finish_sound") or "cuckoo")

    @break_finish_sound.setter
    def break_finish_sound(self, v: str) -> None:
        self.set("break_finish_sound", v)

    @property
    def sound_volume(self) -> float:
        try:
            value = float(self.get("sound_volume"))
        except (TypeError, ValueError):
            value = 0.7
        return max(0.0, min(1.0, value))

    @sound_volume.setter
    def sound_volume(self, v: float):
        try:
            value = float(v)
        except (TypeError, ValueError):
            value = 0.7
        self.set("sound_volume", max(0.0, min(1.0, value)))

    @property
    def preset_work(self) -> int:
        return int(self.get("preset_work"))

    @preset_work.setter
    def preset_work(self, v: int):
        self.set("preset_work", v)

    @property
    def preset_short(self) -> int:
        return int(self.get("preset_short"))

    @preset_short.setter
    def preset_short(self, v: int):
        self.set("preset_short", v)

    @property
    def preset_long(self) -> int:
        return int(self.get("preset_long"))

    @preset_long.setter
    def preset_long(self, v: int):
        self.set("preset_long", v)

    @property
    def last_mode(self) -> str:
        return str(self.get("last_mode"))

    @last_mode.setter
    def last_mode(self, v: str):
        self.set("last_mode", v)

    @property
    def theme_name(self) -> str:
        return str(self.get("theme_name"))

    @theme_name.setter
    def theme_name(self, v: str):
        self.set("theme_name", v)
