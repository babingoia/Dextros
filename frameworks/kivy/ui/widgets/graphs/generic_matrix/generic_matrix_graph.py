"""Renderer puro da matriz. Cacheia os dicts no draw_self; refresh só refatia.
Não constrói zoom, não constrói sticky, não conhece toolbar."""
from typing import Callable, Any

from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from logging import getLogger

from frameworks.kivy.ui.widgets.graphs.generic_matrix.matrix_cell import MatrixCell
from adapters.controllers.dtos.card_view_model import CardViewModel

Builder.load_file("frameworks/kivy/ui/widgets/graphs/generic_matrix/generic_matrix_graph.kv")

logger = getLogger(__name__)


class GenericMatrixGraph(RecycleView):
    __events__ = ("on_data_changed",)

    matrix_cols = NumericProperty(1)     # API (cols + 1)
    layout_cols = NumericProperty(1)     # cols do render atual
    headers_visible = BooleanProperty(True)
    scroll_locked = BooleanProperty(False)

    # Escala injetada (a view binda do zoom). Métricas base vêm da célula.
    scale = NumericProperty(1.0)
    cell_width = NumericProperty(0)
    cell_height = NumericProperty(0)
    cell_spacing = NumericProperty(0)

    def __init__(self, **kwargs):
        logger.info("Initializing GenericMatrixGraph")
        super().__init__(**kwargs)
        # Cache: (corner, col_dicts, row_dicts, body_dicts, n_cols)
        # cell_factory roda UMA vez por draw_self, nunca no refresh/toggle.
        self._parts = None
        self.bind(scale=self._apply_scale)
        self._apply_scale()

    def on_data_changed(self, *args):
        pass

    def _apply_scale(self, *args) -> None:
        c = MatrixCell
        w = c.base_width * self.scale
        h = c.base_height * self.scale
        if c.min_width:
            w = max(w, c.min_width)
        if c.max_width:
            w = min(w, c.max_width)
        if c.min_height:
            h = max(h, c.min_height)
        if c.max_height:
            h = min(h, c.max_height)
        self.cell_width = w
        self.cell_height = h
        self.cell_spacing = c.base_spacing * self.scale

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

        # Único lugar onde cell_factory executa.
        body_dicts = []
        for row_idx in range(len(row_headers)):
            for col_idx in range(len(col_headers)):
                body_dicts.append(
                    cell_factory(row_idx, col_idx, cell_data.get((row_idx, col_idx)))
                )

        self._parts = (
            self.corner_dict(),
            [self._header_dict(c) for c in col_headers],
            [self._header_dict(r) for r in row_headers],
            body_dicts,
            len(col_headers),
        )
        self.matrix_cols = len(col_headers) + 1
        self.refresh()

    def refresh(self) -> None:
        """Refatia o cache pro modo atual. Sem cell_factory, sem rebuild pesado."""
        if self._parts is None:
            return
        corner, col_dicts, row_dicts, body_dicts, n_cols = self._parts

        if self.headers_visible:
            flat = [corner, *col_dicts]
            for i, row_dict in enumerate(row_dicts):
                flat.append(row_dict)
                flat.extend(body_dicts[i * n_cols:(i + 1) * n_cols])
            self.layout_cols = n_cols + 1
        else:
            flat = list(body_dicts)
            self.layout_cols = n_cols

        self.data = flat
        self.dispatch("on_data_changed")

    def header_parts(self):
        """Dicts prontos de headers, pro decorator sticky distribuir."""
        if self._parts is None:
            return [], []
        return self._parts[1], self._parts[2]

    @staticmethod
    def corner_dict() -> dict:
        return {"dextro_text": "", "is_header": True, "is_empty": True, "card_reference": None}

    @staticmethod
    def _header_dict(text: str) -> dict:
        return {"dextro_text": text, "is_header": True, "is_empty": False, "card_reference": None}