"""Zoom genérico. Escuta touch na Window (não precisa de cooperação do target)."""
from time import time

from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.metrics import dp
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.vector import Vector
from logging import getLogger

logger = getLogger(__name__)

_ZOOM_SESSION: dict[str, float] = {}


class Zoom(EventDispatcher):
    zoom_level = NumericProperty(1.0)
    default_zoom = NumericProperty(1.0)
    min_zoom = NumericProperty(0.7)
    max_zoom = NumericProperty(2.0)
    zoom_step = NumericProperty(0.10)
    is_pinching = BooleanProperty(False)
    active = BooleanProperty(True)  # view liga/desliga por screen atual

    persist = BooleanProperty(True)
    session_key = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.persist and self.session_key:
            saved = _ZOOM_SESSION.get(self.session_key)
            if saved is not None:
                self.zoom_level = saved
        self.bind(zoom_level=self._on_zoom_changed)

    def _on_zoom_changed(self, *args):
        if self.persist and self.session_key:
            _ZOOM_SESSION[self.session_key] = float(self.zoom_level)

    def set_zoom(self, value: float) -> None:
        self.zoom_level = self.clamp_zoom(value)

    def zoom_in(self) -> None:
        self.set_zoom(self.zoom_level + self.zoom_step)

    def zoom_out(self) -> None:
        self.set_zoom(self.zoom_level - self.zoom_step)

    def reset_zoom(self) -> None:
        self.set_zoom(self.default_zoom)

    def clamp_zoom(self, value: float) -> float:
        try:
            value = float(value)
        except Exception:
            return float(self.default_zoom)
        return max(self.min_zoom, min(self.max_zoom, value))


class PinchZoom(Zoom):
    double_tap_reset_enabled = BooleanProperty(True)

    def __init__(self, target, **kwargs):
        super().__init__(**kwargs)
        self.target = target
        self._active_touches = {}
        self._pinch_initial_distance = 0.0
        self._pinch_initial_zoom = 1.0
        self._last_tap_time = 0.0
        self._last_tap_pos = (0, 0)

        # Gestos na Window: intercepta ANTES do dispatch pros widgets.
        Window.fbind("on_touch_down", self._win_down)
        Window.fbind("on_touch_move", self._win_move)
        Window.fbind("on_touch_up", self._win_up)

    def release(self) -> None:
        Window.funbind("on_touch_down", self._win_down)
        Window.funbind("on_touch_move", self._win_move)
        Window.funbind("on_touch_up", self._win_up)

    def _win_down(self, window, touch):
        return self._touch_down(touch)

    def _win_move(self, window, touch):
        return self._touch_move(touch)

    def _win_up(self, window, touch):
        self._touch_up(touch)
        return False

    def _touch_down(self, touch) -> bool:
        if not self.active or not self.target.collide_point(*touch.pos):
            return False
        if not self._is_valid_touch(touch):
            return False

        self._active_touches[touch.uid] = touch

        if len(self._active_touches) == 2:
            self._start_pinch()
            return True

        if (
            self.double_tap_reset_enabled
            and not self.is_pinching
            and self._is_double_tap(touch)
        ):
            self.reset_zoom()
            self._last_tap_time = 0.0
            self._last_tap_pos = touch.pos
            return True

        self._last_tap_time = time()
        self._last_tap_pos = touch.pos
        return False

    def _touch_move(self, touch) -> bool:
        if not self.active or touch.uid not in self._active_touches:
            return False

        self._active_touches[touch.uid] = touch

        if len(self._active_touches) >= 2 and not self.is_pinching:
            self._start_pinch()

        if self.is_pinching and len(self._active_touches) >= 2:
            t1, t2 = list(self._active_touches.values())[:2]
            distance = Vector(t1.pos).distance(t2.pos)
            if self._pinch_initial_distance > 0 and distance > 0:
                self.set_zoom(self._pinch_initial_zoom * (distance / self._pinch_initial_distance))
            return True
        return False

    def _touch_up(self, touch) -> None:
        if touch.uid in self._active_touches:
            del self._active_touches[touch.uid]
        if self.is_pinching and len(self._active_touches) < 2:
            self.is_pinching = False
            self._pinch_initial_distance = 0.0
            self._pinch_initial_zoom = self.zoom_level

    def _start_pinch(self) -> None:
        touches = list(self._active_touches.values())[:2]
        if len(touches) < 2:
            return
        self.is_pinching = True
        self._pinch_initial_distance = Vector(touches[0].pos).distance(touches[1].pos) or 1.0
        self._pinch_initial_zoom = self.zoom_level

    def _is_double_tap(self, touch) -> bool:
        if not self._last_tap_time:
            return False
        if time() - self._last_tap_time > 0.30:
            return False
        return Vector(touch.pos).distance(self._last_tap_pos) <= dp(26)

    @staticmethod
    def _is_valid_touch(touch) -> bool:
        if getattr(touch, "is_mouse_scrolling", False):
            return False
        return getattr(touch, "button", None) in (None, "left", "touch", "unknown")