from __future__ import annotations

from time import time
from typing import Callable, Any, Optional
from logging import getLogger

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.properties import (
    NumericProperty,
    BooleanProperty,
    StringProperty,
    ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.vector import Vector

from frameworks.kivy.ui.app_theme import space
from frameworks.kivy.ui.widgets.graphs.matrix_cell import MatrixCell
from adapters.controllers.dtos.card_view_model import CardViewModel

logger = getLogger(__name__)

_ZOOM_SESSION_STATE: dict[str, float] = {}
_STICKY_SESSION_STATE: dict[str, bool] = {}


class ToolButton(Button):
    active_state = BooleanProperty(False)


class ZoomControls(BoxLayout):
    graph = ObjectProperty(None, allownone=True)


Factory.register("MatrixCell", cls=MatrixCell)
Factory.register("ToolButton", cls=ToolButton)
Factory.register("ZoomControls", cls=ZoomControls)

Builder.load_file("frameworks/kivy/ui/widgets/graphs/generic_matrix_graph.kv")


class GenericMatrixGraph(BoxLayout):
    matrix_cols = NumericProperty(1)

    zoom_level = NumericProperty(1.0)
    default_zoom = NumericProperty(1.0)
    min_zoom = NumericProperty(0.7)
    max_zoom = NumericProperty(2.0)
    zoom_step = NumericProperty(0.10)
    double_tap_reset_enabled = BooleanProperty(True)

    sticky_headers = BooleanProperty(False)

    show_zoom_controls = BooleanProperty(True)
    controls_container = ObjectProperty(None, allownone=True)

    base_cell_width = NumericProperty(0)
    base_cell_height = NumericProperty(0)
    base_spacing = NumericProperty(0)

    min_cell_width = NumericProperty(0)
    min_cell_height = NumericProperty(0)
    max_cell_width = NumericProperty(0)
    max_cell_height = NumericProperty(0)

    cell_width = NumericProperty(0)
    cell_height = NumericProperty(0)
    cell_spacing = NumericProperty(0)

    is_pinching = BooleanProperty(False)

    persist_zoom = BooleanProperty(True)
    zoom_session_key = StringProperty("GenericMatrixGraph")

    def __init__(self, container: Optional[Any] = None, **kwargs):
        logger.info("Initializing GenericMatrixGraph")
        super().__init__(**kwargs)
        self.orientation = "vertical"

        self._container = container

        if self.base_cell_width == 0:
            self.base_cell_width = dp(152)
        if self.base_cell_height == 0:
            self.base_cell_height = dp(44)
        if self.base_spacing == 0:
            self.base_spacing = dp(4)

        self._active_touches = {}
        self._pinch_initial_distance = 0.0
        self._pinch_initial_zoom = 1.0
        self._last_tap_time = 0.0
        self._last_tap_pos = (0, 0)

        self._last_draw = None
        self._n_cols = 0

        self._corner = None
        self._top_view = None
        self._left_view = None
        self._body_view = None
        self._top_layout = None
        self._left_layout = None
        self._body_layout = None
        self._top_row = None
        self._bottom_row = None
        self._outer = None
        self._layouts = []

        # Toolbar / wrapper (para poder remanejar depois)
        self._toolbar = None
        self._wrapper = None
        self._embed_container = None

        if self.persist_zoom and self.zoom_session_key:
            saved_zoom = _ZOOM_SESSION_STATE.get(self.zoom_session_key)
            if saved_zoom is not None:
                self.zoom_level = saved_zoom
            saved_sticky = _STICKY_SESSION_STATE.get(self.zoom_session_key)
            if saved_sticky is not None:
                self.sticky_headers = saved_sticky

        # Dimensões efetivas ANTES de montar qualquer view.
        z = self._clamp_zoom(self.zoom_level)
        self.cell_width = self.base_cell_width * z
        self.cell_height = self.base_cell_height * z
        self.cell_spacing = self.base_spacing * z

        self.bind(
            zoom_level=self._apply_zoom,
            base_cell_width=self._apply_zoom,
            base_cell_height=self._apply_zoom,
            base_spacing=self._apply_zoom,
            min_zoom=self._apply_zoom,
            max_zoom=self._apply_zoom,
            min_cell_width=self._apply_zoom,
            min_cell_height=self._apply_zoom,
            max_cell_width=self._apply_zoom,
            max_cell_height=self._apply_zoom,
            sticky_headers=self._on_sticky_changed,
        )

        self._assemble()

        if self._container:
            self.embed_in(self._container)

    # ------------------------------------------------------------------
    # Montagem + toolbar (com retry anti-timing)
    # ------------------------------------------------------------------
    def embed_in(self, container) -> None:
        if not self.show_zoom_controls:
            container.add_widget(self)
            return

        self._embed_container = container
        self._toolbar = ZoomControls(graph=self)

        slot = self.controls_container or self._find_controls_slot(container)
        if slot is not None:
            self._place_in_slot(slot)
        else:
            # Fallback imediato + retry: o container pode ainda não estar
            # pendurado na árvore da screen (timing de composição).
            self._wrapper = BoxLayout(orientation="vertical", spacing=space("sm"))
            self._wrapper.add_widget(self._toolbar)
            self._wrapper.add_widget(self)
            container.add_widget(self._wrapper)
            Clock.schedule_once(lambda dt: self._retry_slot(0), 0)

    def _retry_slot(self, attempt=0) -> None:
        if self._wrapper is None:
            return  # já foi pro slot

        slot = self.controls_container or self._find_controls_slot(self._embed_container)
        if slot is not None:
            logger.info("  Slot encontrado no retry: movendo toolbar para o header")
            self._wrapper.remove_widget(self._toolbar)
            self._wrapper.remove_widget(self)
            parent = self._wrapper.parent
            if parent is not None:
                parent.remove_widget(self._wrapper)
            self._wrapper = None
            self._place_in_slot(slot)
            return

        if attempt < 5:
            Clock.schedule_once(lambda dt, a=attempt + 1: self._retry_slot(a), 0.2)

    def _place_in_slot(self, slot) -> None:
        slot.clear_widgets()
        slot.add_widget(self._toolbar)
        self._embed_container.add_widget(self)
        self._wrapper = None

    def _find_controls_slot(self, container):
        """Sobe a árvore procurando 'header_actions' no ids de QUALQUER ancestral."""
        node = container
        chain = []
        while node is not None:
            chain.append(type(node).__name__)
            ids = getattr(node, "ids", None)
            if ids:
                slot = ids.get("header_actions")
                if slot is not None:
                    logger.info(f"  Slot 'header_actions' encontrado em: {type(node).__name__}")
                    return slot
            node = getattr(node, "parent", None)

        logger.info(f"  Slot NÃO encontrado. Cadeia percorrida: {' -> '.join(chain)}")
        return None

    # ------------------------------------------------------------------
    # Views internas (via KV, o caminho que funciona)
    # ------------------------------------------------------------------
    def _make_view(self, cols=1, scroll_x=False, scroll_y=False):
        rv = Factory.get("MatrixInnerView")()
        rv.do_scroll_x = scroll_x
        rv.do_scroll_y = scroll_y

        layout = rv.layout_manager or rv.children[0]
        layout.cols = cols
        layout.spacing = self.cell_spacing
        layout.default_size = (self.cell_width, self.cell_height)
        return rv, layout

    def _assemble(self) -> None:
        self.clear_widgets()
        self._corner = self._top_view = self._left_view = None
        self._top_layout = self._left_layout = self._body_layout = None
        self._top_row = self._bottom_row = self._outer = None
        self._layouts = []

        if not self.sticky_headers:
            self._body_view, self._body_layout = self._make_view(
                cols=self.matrix_cols, scroll_x=True, scroll_y=True
            )
            self._layouts = [self._body_layout]
            self.add_widget(self._body_view)
            return

        self._corner = MatrixCell(is_header=True, is_empty=True)
        self._corner.size_hint = (None, None)

        self._top_view, self._top_layout = self._make_view(cols=max(self._n_cols, 1))
        self._left_view, self._left_layout = self._make_view(cols=1)
        self._left_view.size_hint_x = None
        self._body_view, self._body_layout = self._make_view(
            cols=max(self._n_cols, 1), scroll_x=True, scroll_y=True
        )

        self._body_view.bind(
            scroll_x=lambda inst, val: setattr(self._top_view, "scroll_x", val),
            scroll_y=lambda inst, val: setattr(self._left_view, "scroll_y", val),
        )

        sp = self.cell_spacing

        self._top_row = BoxLayout(orientation="horizontal", spacing=sp)
        self._top_row.size_hint_y = None
        self._top_row.add_widget(self._corner)
        self._top_row.add_widget(self._top_view)

        self._bottom_row = BoxLayout(orientation="horizontal", spacing=sp)
        self._bottom_row.add_widget(self._left_view)
        self._bottom_row.add_widget(self._body_view)

        self._outer = BoxLayout(orientation="vertical", spacing=sp)
        self._outer.add_widget(self._top_row)
        self._outer.add_widget(self._bottom_row)

        self._layouts = [self._top_layout, self._left_layout, self._body_layout]
        self.add_widget(self._outer)
        self._apply_metrics()

    def _apply_metrics(self, *args) -> None:
        cw, ch, sp = self.cell_width, self.cell_height, self.cell_spacing
        for layout in self._layouts:
            layout.default_size = (cw, ch)
            layout.spacing = sp

        if self._corner is not None:
            self._corner.width = cw
            self._corner.height = ch
        if self._top_row is not None:
            self._top_row.height = ch
            self._top_row.spacing = sp
        if self._bottom_row is not None:
            self._bottom_row.spacing = sp
        if self._left_view is not None:
            self._left_view.width = cw
        if self._outer is not None:
            self._outer.spacing = sp

    def _on_sticky_changed(self, *args) -> None:
        if self.persist_zoom and self.zoom_session_key:
            _STICKY_SESSION_STATE[self.zoom_session_key] = bool(self.sticky_headers)
        self._assemble()
        self._redistribute()

    def toggle_sticky_headers(self) -> None:
        self.sticky_headers = not self.sticky_headers

    # ------------------------------------------------------------------
    # Zoom
    # ------------------------------------------------------------------
    def set_zoom(self, value: float) -> None:
        self.zoom_level = self._clamp_zoom(value)

    def zoom_in(self) -> None:
        self.set_zoom(self.zoom_level + self.zoom_step)

    def zoom_out(self) -> None:
        self.set_zoom(self.zoom_level - self.zoom_step)

    def reset_zoom(self) -> None:
        self.set_zoom(self.default_zoom)

    def on_zoom_session_key(self, *args) -> None:
        if self.persist_zoom or not self.zoom_session_key:
            return
        saved_zoom = _ZOOM_SESSION_STATE.get(self.zoom_session_key)
        if saved_zoom is not None:
            self.set_zoom(saved_zoom)
        else:
            _ZOOM_SESSION_STATE[self.zoom_session_key] = float(self.zoom_level)

    def _clamp_zoom(self, value: float) -> float:
        try:
            value = float(value)
        except Exception:
            return float(self.default_zoom)

        min_z = float(self.min_zoom)
        max_z = float(self.max_zoom)
        if min_z > max_z:
            min_z, max_z = max_z, min_z

        if self.base_cell_width > 0:
            if self.min_cell_width > 0:
                min_z = max(min_z, self.min_cell_width / self.base_cell_width)
            if self.max_cell_width > 0:
                max_z = min(max_z, self.max_cell_width / self.base_cell_width)

        if self.base_cell_height > 0:
            if self.min_cell_height > 0:
                min_z = max(min_z, self.min_cell_height / self.base_cell_height)
            if self.max_cell_height > 0:
                max_z = min(max_z, self.max_cell_height / self.base_cell_height)

        if min_z > max_z:
            min_z = max_z

        return max(min_z, min(max_z, value))

    def _apply_zoom(self, *args) -> None:
        z = self._clamp_zoom(self.zoom_level)

        if abs(float(z) - float(self.zoom_level)) > 0.0005:
            self.zoom_level = z
            return

        self.cell_width = self.base_cell_width * z
        self.cell_height = self.base_cell_height * z
        self.cell_spacing = self.base_spacing * z

        if self.persist_zoom and self.zoom_session_key:
            _ZOOM_SESSION_STATE[self.zoom_session_key] = float(z)

        self._apply_metrics()

    # ------------------------------------------------------------------
    # Dados
    # ------------------------------------------------------------------
    def draw_self(
        self,
        row_headers: list[str],
        col_headers: list[str],
        cell_data: dict[tuple[int, int], CardViewModel],
        cell_factory: Callable[[int, int, Any], dict],
    ) -> None:
        logger.info(f"Populating Matrix: {len(row_headers)} rows x {len(col_headers)} cols")

        if not row_headers or not col_headers:
            logger.warning("Matrix headers are empty.")

        self._last_draw = (row_headers, col_headers, cell_data, cell_factory)
        self._n_cols = len(col_headers)
        self.matrix_cols = len(col_headers) + 1

        self._redistribute()

    def _redistribute(self) -> None:
        if self._last_draw is None or self._body_view is None:
            return

        row_headers, col_headers, cell_data, cell_factory = self._last_draw

        if not self.sticky_headers:
            flat_data = [self._create_corner_dict()]
            for col_header in col_headers:
                flat_data.append(self._create_header_dict(col_header))
            for row_idx, row_header in enumerate(row_headers):
                flat_data.append(self._create_header_dict(row_header))
                for col_idx in range(len(col_headers)):
                    payload = cell_data.get((row_idx, col_idx))
                    flat_data.append(cell_factory(row_idx, col_idx, payload))

            self._body_layout.cols = len(col_headers) + 1
            self._body_view.data = flat_data
            return

        self._top_layout.cols = max(len(col_headers), 1)
        self._body_layout.cols = max(len(col_headers), 1)

        self._top_view.data = [self._create_header_dict(c) for c in col_headers]
        self._left_view.data = [self._create_header_dict(r) for r in row_headers]

        cells = []
        for row_idx in range(len(row_headers)):
            for col_idx in range(len(col_headers)):
                payload = cell_data.get((row_idx, col_idx))
                cells.append(cell_factory(row_idx, col_idx, payload))

        self._body_view.data = cells

    def _create_corner_dict(self) -> dict:
        return {
            "dextro_text": "",
            "is_header": True,
            "is_empty": True,
            "card_reference": None,
        }

    def _create_header_dict(self, text: str) -> dict:
        return {
            "dextro_text": text,
            "is_header": True,
            "is_empty": False,
            "card_reference": None,
        }

    # ------------------------------------------------------------------
    # Touch: pinch + double tap
    # ------------------------------------------------------------------
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        if self._is_valid_touch(touch):
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

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._is_valid_touch(touch) and touch.uid in self._active_touches:
            self._active_touches[touch.uid] = touch

            if len(self._active_touches) >= 2 and not self.is_pinching:
                self._start_pinch()

            if self.is_pinching and len(self._active_touches) >= 2:
                t1, t2 = list(self._active_touches.values())[:2]
                distance = self._touch_distance(t1, t2)

                if self._pinch_initial_distance > 0 and distance > 0:
                    ratio = distance / self._pinch_initial_distance
                    self.set_zoom(self._pinch_initial_zoom * ratio)

                return True

        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.uid in self._active_touches:
            del self._active_touches[touch.uid]

        if self.is_pinching and len(self._active_touches) < 2:
            self.is_pinching = False
            self._pinch_initial_distance = 0.0
            self._pinch_initial_zoom = self.zoom_level

        return super().on_touch_up(touch)

    def _is_valid_touch(self, touch) -> bool:
        if getattr(touch, "is_mouse_scrolling", False):
            return False
        button = getattr(touch, "button", None)
        if button not in (None, "left", "touch", "unknown"):
            return False
        return True

    def _start_pinch(self) -> None:
        touches = list(self._active_touches.values())[:2]
        if len(touches) < 2:
            return
        self.is_pinching = True
        self._pinch_initial_distance = self._touch_distance(touches[0], touches[1]) or 1.0
        self._pinch_initial_zoom = self.zoom_level

    def _is_double_tap(self, touch) -> bool:
        if not self._last_tap_time:
            return False
        if time() - self._last_tap_time > 0.30:
            return False
        return Vector(touch.pos).distance(self._last_tap_pos) <= dp(26)

    @staticmethod
    def _touch_distance(t1, t2) -> float:
        return Vector(t1.pos).distance(t2.pos)