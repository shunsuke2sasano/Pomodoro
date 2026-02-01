"""
Main widget for the desktop dial timer.
"""
from __future__ import annotations

import math

from PySide6.QtCore import Qt, QPoint, QRectF
from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QPen,
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QRegion,
    QMouseEvent,
    QActionGroup,
)
from PySide6.QtWidgets import QWidget, QMenu

from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_RADIUS,
    SHADOW_OFFSET,
    SHADOW_BLUR,
    DISC_MARGIN,
    TICK_LENGTH_MAJOR,
    TICK_LENGTH_MINOR,
    TICK_WIDTH_MAJOR,
    TICK_WIDTH_MINOR,
    C_BG_OUTER,
    C_BG_DISC,
    C_BG_INNER,
    C_TICK_MAJOR,
    C_TICK_MINOR,
    C_TEXT_TIME,
    C_TEXT_MODE,
    C_TEXT_SET,
    C_SHADOW,
    FONT_FAMILY,
    FONT_SIZE_TIME,
    FONT_SIZE_MODE,
    FONT_SIZE_SET,
    MODE_WORK,
    MODE_SHORT,
    MODE_LONG,
    MODE_LABELS,
    MAX_DIAL_MIN,
    THEMES,
    DEFAULT_THEME,
)
from settings import Settings
from timer_engine import TimerEngine, TimerState
from notifier import show_notification, play_sound


class PomodoroWidget(QWidget):
    """Main dial timer widget."""

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._engine = TimerEngine(settings, self)

        # Drag state
        self._press_pos: QPoint | None = None
        self._press_global: QPoint | None = None
        self._drag_mode: str | None = None  # "dial" or "window"
        self._dragging: bool = False
        self._window_drag_offset: QPoint = QPoint(0, 0)

        self._setup_window()

        self._engine.tick.connect(self._on_tick)
        self._engine.finished.connect(self._on_finished)
        self._engine.state_changed.connect(self.update)
        self._engine.mode_changed.connect(self.update)

    def _setup_window(self) -> None:
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        flags = Qt.Window | Qt.FramelessWindowHint | Qt.Tool
        if self._settings.always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        # Allow keyboard focus (Space key)
        self.setFocusPolicy(Qt.StrongFocus)

        # Restore position
        self.move(self._settings.window_x, self._settings.window_y)

        # Rounded mask
        self._apply_round_mask()

        # Transparent background (for shadow)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def _apply_round_mask(self) -> None:
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            WINDOW_RADIUS, WINDOW_RADIUS,
        )
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def _on_tick(self, remaining: int) -> None:
        self.update()

    def _on_finished(self, mode: str) -> None:
        label = MODE_LABELS.get(mode, mode)
        if mode == MODE_WORK:
            title = "Focus complete"
            msg = f"{label} finished. Time for a break."
        else:
            title = "Break complete"
            msg = f"{label} finished. Time to focus."

        show_notification(title, msg)
        if self._settings.sound_on:
            # Focus/Breakで終了音を分ける
            if mode == MODE_WORK:
                sound_key = self._settings.focus_finish_sound
            else:
                sound_key = self._settings.break_finish_sound
            play_sound(sound_key, volume=self._settings.sound_volume)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._press_pos = event.position().toPoint()
            self._press_global = event.globalPosition().toPoint()
            self._dragging = False
            if self._is_in_dial(self._press_pos):
                self._drag_mode = "dial"
            else:
                self._drag_mode = "window"
                self._window_drag_offset = event.position().toPoint()
            event.accept()
        elif event.button() == Qt.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._press_pos is not None and (event.buttons() & Qt.LeftButton):
            if not self._dragging:
                delta = event.position().toPoint() - self._press_pos
                if abs(delta.x()) > 3 or abs(delta.y()) > 3:
                    self._dragging = True

            if self._drag_mode == "dial":
                if self._dragging:
                    self._update_dial_from_pos(event.position().toPoint())
            elif self._drag_mode == "window":
                if self._dragging:
                    new_pos = event.globalPosition().toPoint() - self._window_drag_offset
                    self.move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            if self._press_pos is not None and not self._dragging and self._is_in_center(self._press_pos):
                self._engine.start_or_pause()
            self._press_pos = None
            self._press_global = None
            self._drag_mode = None
            self._dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event) -> None:
        super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        self._save_position()
        self._settings.save()
        event.accept()

    def _update_dial_from_pos(self, pos: QPoint) -> None:
        minutes = self._pos_to_minutes(pos)
        self._engine.set_duration(minutes * 60)
        self.update()

    def _pos_to_minutes(self, pos: QPoint) -> int:
        cx, cy = self.width() / 2, self.height() / 2
        dx = pos.x() - cx
        dy = pos.y() - cy
        ang = math.atan2(dy, dx)  # right = 0
        ang += math.pi / 2        # 12 o'clock = 0
        if ang < 0:
            ang += 2 * math.pi
        ratio = ang / (2 * math.pi)
        minutes = round(ratio * MAX_DIAL_MIN)
        return max(0, min(MAX_DIAL_MIN, minutes))

    def _minutes_to_angle(self, minutes: float) -> float:
        minutes = max(0.0, min(MAX_DIAL_MIN, minutes))
        ratio = minutes / MAX_DIAL_MIN
        return ratio * 2 * math.pi - math.pi / 2

    def _is_in_dial(self, pos: QPoint) -> bool:
        cx, cy = self.width() / 2, self.height() / 2
        dx = pos.x() - cx
        dy = pos.y() - cy
        r = math.hypot(dx, dy)
        outer = min(self.width(), self.height()) / 2 - DISC_MARGIN - max(
            TICK_LENGTH_MAJOR, TICK_LENGTH_MINOR
        ) - 2
        return r <= outer

    def _is_in_center(self, pos: QPoint) -> bool:
        cx, cy = self.width() / 2, self.height() / 2
        dx = pos.x() - cx
        dy = pos.y() - cy
        r = math.hypot(dx, dy)
        radius = min(self.width(), self.height()) / 2 - DISC_MARGIN - max(
            TICK_LENGTH_MAJOR, TICK_LENGTH_MINOR
        ) - 2
        inner_radius = radius * 0.52
        return r <= inner_radius

    def _current_theme(self) -> dict:
        base = THEMES.get(DEFAULT_THEME) or next(iter(THEMES.values()), {})
        theme = THEMES.get(self._settings.theme_name, base)
        merged = dict(base) if isinstance(base, dict) else {}
        if isinstance(theme, dict):
            merged.update(theme)
        return merged

    def _with_alpha(self, color: QColor, alpha: int) -> QColor:
        c = QColor(color)
        c.setAlpha(alpha)
        return c

    def _set_theme(self, theme_name: str) -> None:
        if theme_name not in THEMES:
            theme_name = DEFAULT_THEME
        self._settings.theme_name = theme_name
        self._settings.save()
        self.update()

    def _show_context_menu(self, pos: QPoint) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(self._context_menu_stylesheet())

        menu.addAction("Reset", self._engine.reset)
        menu.addSeparator()

        mode_menu = menu.addMenu("Mode")
        for mode_key, mode_label in MODE_LABELS.items():
            act = mode_menu.addAction(mode_label)
            act.setCheckable(True)
            act.setChecked(self._engine.mode == mode_key)
            act.triggered.connect(lambda checked, m=mode_key: self._engine.set_mode(m))

        menu.addSeparator()

        preset_menu = menu.addMenu("Presets")
        preset_menu.addAction(
            f"Work: {self._settings.preset_work} min",
            lambda: self._change_preset("work"),
        )
        preset_menu.addAction(
            f"Short Break: {self._settings.preset_short} min",
            lambda: self._change_preset("short"),
        )
        preset_menu.addAction(
            f"Long Break: {self._settings.preset_long} min",
            lambda: self._change_preset("long"),
        )

        menu.addSeparator()

        theme_menu = menu.addMenu("Theme")
        theme_group = QActionGroup(theme_menu)
        theme_group.setExclusive(True)
        for theme_key, theme in THEMES.items():
            label = theme.get("label", theme_key)
            act = theme_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(self._settings.theme_name == theme_key)
            act.setActionGroup(theme_group)
            act.triggered.connect(lambda checked, t=theme_key: self._set_theme(t))

        menu.addSeparator()
        # Focus/Break で終了音を分ける
        sound_labels = {
            "lion": "ライオン",
            "mountain": "夏の山",
            "tombi": "トンビ",
            "cuckoo": "カッコウ",
        }
        focus_sound_menu = menu.addMenu("Focus Sound")
        focus_group = QActionGroup(focus_sound_menu)
        focus_group.setExclusive(True)
        for key, label in sound_labels.items():
            act = focus_sound_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(self._settings.focus_finish_sound == key)
            act.setActionGroup(focus_group)
            act.triggered.connect(lambda checked, k=key: self._set_focus_finish_sound(k))

        break_sound_menu = menu.addMenu("Break Sound")
        break_group = QActionGroup(break_sound_menu)
        break_group.setExclusive(True)
        
        for key, label in sound_labels.items():
            act = break_sound_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(self._settings.break_finish_sound == key)
            act.setActionGroup(break_group)
            act.triggered.connect(lambda checked, k=key: self._set_break_finish_sound(k))

        menu.addSeparator()

        volume_menu = menu.addMenu("Volume")
        volume_group = QActionGroup(volume_menu)
        volume_group.setExclusive(True)
        volume_options = [0.3, 0.5, 0.7, 0.9]
        current_volume = float(self._settings.sound_volume)
        closest_volume = min(volume_options, key=lambda v: abs(v - current_volume))
        for v in volume_options:
            label = f"{int(v * 100)}%"
            act = volume_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(v == closest_volume)
            act.setActionGroup(volume_group)
            act.triggered.connect(lambda *_, val=v: self._set_sound_volume(val))

        menu.addSeparator()

        transparency_menu = menu.addMenu("Transparency")
        transparency_group = QActionGroup(transparency_menu)
        transparency_group.setExclusive(True)
        percent_options = list(range(10, 101, 10))
        current_alpha = int(self._settings.bg_opacity)
        alpha_values = [int(255 * p / 100) for p in percent_options]
        closest_alpha = min(alpha_values, key=lambda a: abs(a - current_alpha))
        for p, alpha in zip(percent_options, alpha_values):
            label = f"{p}%"
            if p == 100:
                label = "100% (Solid)"
            act = transparency_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(alpha == closest_alpha)
            act.setActionGroup(transparency_group)
            act.triggered.connect(lambda checked, v=alpha: self._set_bg_opacity(v))

        menu.addSeparator()

        aot_action = menu.addAction("Always on Top")
        aot_action.setCheckable(True)
        aot_action.setChecked(self._settings.always_on_top)
        aot_action.triggered.connect(self._toggle_always_on_top)

        sound_action = menu.addAction("Sound On/Off")
        sound_action.setCheckable(True)
        sound_action.setChecked(self._settings.sound_on)
        sound_action.triggered.connect(self._toggle_sound)

        menu.addSeparator()
        menu.addAction("Quit", self.close)

        menu.exec(pos)

    def _change_preset(self, preset_type: str) -> None:
        from PySide6.QtWidgets import QInputDialog

        current_map = {
            "work": ("Work minutes", self._settings.preset_work),
            "short": ("Short break minutes", self._settings.preset_short),
            "long": ("Long break minutes", self._settings.preset_long),
        }
        label, current = current_map[preset_type]
        value, ok = QInputDialog.getInt(
            self, "Change preset", label,
            current, 1, 120, 1
        )
        if ok:
            if preset_type == "work":
                self._settings.preset_work = value
            elif preset_type == "short":
                self._settings.preset_short = value
            else:
                self._settings.preset_long = value

            if (preset_type == "work" and self._engine.mode == MODE_WORK) or \
               (preset_type == "short" and self._engine.mode == MODE_SHORT) or \
               (preset_type == "long" and self._engine.mode == MODE_LONG):
                self._engine.set_mode(self._engine.mode)
            self._settings.save()

    def _toggle_always_on_top(self, checked: bool) -> None:
        self._settings.always_on_top = checked
        flags = self.windowFlags()
        if checked:
            flags |= Qt.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        self._settings.save()

    def _toggle_sound(self, checked: bool) -> None:
        self._settings.sound_on = checked
        self._settings.save()

    def _set_finish_sound(self, key: str) -> None:
        self._settings.finish_sound = key
        self._settings.save()
    
    def _set_focus_finish_sound(self, key: str) -> None:
        self._settings.focus_finish_sound = key
        self._settings.save()

    def _set_break_finish_sound(self, key: str) -> None:
        self._settings.break_finish_sound = key
        self._settings.save()

    def _set_sound_volume(self, value: float) -> None:
        self._settings.sound_volume = value
        self._settings.save()

    def _set_bg_opacity(self, value: int) -> None:
        self._settings.bg_opacity = value
        self._settings.save()
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)

        w, h = self.width(), self.height()

        self._draw_shadow(p, w, h)
        self._draw_background(p, w, h)
        self._draw_ticks(p, w, h)
        self._draw_disc(p, w, h)
        self._draw_hand(p, w, h)
        self._draw_text(p, w, h)

        p.end()

    def _draw_shadow(self, p: QPainter, w: int, h: int) -> None:
        theme = self._current_theme()
        alpha = int(self._settings.bg_opacity)
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(
            QRectF(SHADOW_OFFSET, SHADOW_OFFSET, w, h),
            WINDOW_RADIUS, WINDOW_RADIUS,
        )
        p.save()
        p.setPen(Qt.NoPen)
        shadow_alpha = min(alpha, 120)
        p.setBrush(QBrush(self._with_alpha(theme.get("shadow", C_SHADOW), shadow_alpha)))
        p.drawPath(shadow_path)
        p.restore()

    def _draw_background(self, p: QPainter, w: int, h: int) -> None:
        theme = self._current_theme()
        alpha = int(self._settings.bg_opacity)
        bg_path = QPainterPath()
        bg_path.addRoundedRect(
            QRectF(0, 0, w, h),
            WINDOW_RADIUS, WINDOW_RADIUS,
        )
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(self._with_alpha(theme.get("bg_outer", C_BG_OUTER), alpha)))
        p.drawPath(bg_path)
        p.restore()

    def _draw_ticks(self, p: QPainter, w: int, h: int) -> None:
        theme = self._current_theme()
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - DISC_MARGIN

        p.save()
        total_minutes = MAX_DIAL_MIN
        for i in range(total_minutes):
            angle_deg = i * (360.0 / total_minutes)
            angle_rad = math.radians(angle_deg - 90)

            is_major = (i % 5 == 0)
            tick_len = TICK_LENGTH_MAJOR if is_major else TICK_LENGTH_MINOR
            color = theme.get("tick_major", C_TICK_MAJOR) if is_major else theme.get("tick_minor", C_TICK_MINOR)
            width = TICK_WIDTH_MAJOR if is_major else TICK_WIDTH_MINOR

            x_outer = cx + radius * math.cos(angle_rad)
            y_outer = cy + radius * math.sin(angle_rad)
            x_inner = cx + (radius - tick_len) * math.cos(angle_rad)
            y_inner = cy + (radius - tick_len) * math.sin(angle_rad)

            pen = QPen(color, width)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawLine(
                QPoint(round(x_outer), round(y_outer)),
                QPoint(round(x_inner), round(y_inner)),
            )

        p.restore()

    def _draw_disc(self, p: QPainter, w: int, h: int) -> None:
        theme = self._current_theme()
        alpha = int(self._settings.bg_opacity)
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - DISC_MARGIN - max(TICK_LENGTH_MAJOR, TICK_LENGTH_MINOR) - 2
        disc_rect = QRectF(
            cx - radius, cy - radius,
            radius * 2, radius * 2,
        )

        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(self._with_alpha(theme.get("bg_disc", C_BG_DISC), alpha)))
        p.drawEllipse(disc_rect)
        p.restore()

        engine = self._engine
        max_seconds = MAX_DIAL_MIN * 60
        if max_seconds > 0:
            ratio = max(0.0, min(1.0, engine.remaining / max_seconds))
        else:
            ratio = 0.0

        if ratio > 0.0:
            start_angle_qt16 = 90 * 16
            span_qt16 = -int(ratio * 360 * 16)
            arc_color = theme.get("arc", C_BG_DISC)

            p.save()
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(arc_color))
            p.drawPie(disc_rect, start_angle_qt16, span_qt16)
            p.restore()

        inner_radius = radius * 0.52
        inner_rect = QRectF(
            cx - inner_radius, cy - inner_radius,
            inner_radius * 2, inner_radius * 2,
        )
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(self._with_alpha(theme.get("bg_inner", C_BG_INNER), alpha)))
        p.drawEllipse(inner_rect)
        p.restore()

    def _draw_hand(self, p: QPainter, w: int, h: int) -> None:
        theme = self._current_theme()
        cx, cy = w / 2, h / 2
        minutes = max(0.0, min(MAX_DIAL_MIN, self._engine.remaining / 60))
        angle_rad = self._minutes_to_angle(minutes)
        length = min(w, h) / 2 - DISC_MARGIN - max(TICK_LENGTH_MAJOR, TICK_LENGTH_MINOR) - 10
        x = cx + length * math.cos(angle_rad)
        y = cy + length * math.sin(angle_rad)

        p.save()
        pen = QPen(theme.get("hand", C_TEXT_TIME), 2)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawLine(QPoint(round(cx), round(cy)), QPoint(round(x), round(y)))
        p.restore()

    def _draw_text(self, p: QPainter, w: int, h: int) -> None:
        theme = self._current_theme()
        cx, cy = w / 2, h / 2
        engine = self._engine

        remaining = engine.remaining
        mm = remaining // 60
        ss = remaining % 60
        time_str = f"{mm:02d}:{ss:02d}"

        mode_label = MODE_LABELS.get(engine.mode, "")

        font_mode = QFont(FONT_FAMILY, FONT_SIZE_MODE, QFont.Medium)
        p.save()
        p.setFont(font_mode)
        p.setPen(QPen(theme.get("text_mode", C_TEXT_MODE)))
        fm = QFontMetrics(font_mode)
        mode_w = fm.horizontalAdvance(mode_label)
        p.drawText(
            round(cx - mode_w / 2),
            round(cy - 18),
            mode_label,
        )
        p.restore()

        font_time = QFont(FONT_FAMILY, FONT_SIZE_TIME, QFont.Light)
        p.save()
        p.setFont(font_time)
        p.setPen(QPen(theme.get("text_time", C_TEXT_TIME)))
        fm_time = QFontMetrics(font_time)
        time_w = fm_time.horizontalAdvance(time_str)
        p.drawText(
            round(cx - time_w / 2),
            round(cy + fm_time.ascent() / 2 - 2),
            time_str,
        )
        p.restore()

        set_str = f"Set {engine.set_count}"
        font_set = QFont(FONT_FAMILY, FONT_SIZE_SET, QFont.Normal)
        p.save()
        p.setFont(font_set)
        p.setPen(QPen(theme.get("text_set", C_TEXT_SET)))
        fm_set = QFontMetrics(font_set)
        set_w = fm_set.horizontalAdvance(set_str)
        p.drawText(
            round(cx - set_w / 2),
            round(cy + 36),
            set_str,
        )
        p.restore()

    def _save_position(self) -> None:
        pos = self.pos()
        self._settings.window_x = pos.x()
        self._settings.window_y = pos.y()

    def _context_menu_stylesheet(self) -> str:
        return """
        QMenu {
            background-color: #2a2d33;
            border: 1px solid #3a3e47;
            border-radius: 6px;
            padding: 4px;
            color: #e0e0e5;
            font-family: "Segoe UI";
            font-size: 12px;
        }
        QMenu::item {
            padding: 6px 20px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #3a3e4a;
        }
        QMenu::item:disabled {
            color: #666;
        }
        QMenu::separator {
            height: 1px;
            background-color: #3a3e47;
            margin: 2px 8px;
        }
        QMenu::indicator:checked {
            image: none;
            border-left: 3px solid #60b48c;
            padding-left: 2px;
        }
        """
