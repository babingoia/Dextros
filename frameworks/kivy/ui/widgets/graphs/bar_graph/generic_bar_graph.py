from typing import Callable

from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from logging import getLogger

from adapters.controllers.dtos.single_row_matrix_view import SingleRowMatrixView
from frameworks.kivy.ui import app_theme
from frameworks.kivy.ui.widgets.graphs.bar_graph.bar_cell import BarCell

Builder.load_file("frameworks/kivy/ui/widgets/graphs/bar_graph/generic_bar_graph.kv")

logger = getLogger(__name__)


class GenericBarGraph(RecycleView):
    __events__ = ("on_data_changed",)

    scroll_locked = BooleanProperty(False)
    layout_cols = NumericProperty(1)

    # Dimensões explícitas do conteúdo. Fluxo unidirecional:
    # (width da view + dados) -> properties -> layout. Sem minimum_width.
    cell_width = NumericProperty(0)
    content_width = NumericProperty(0)
    content_height = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._n_cols = 0
        self.content_height = (
            app_theme.widget('bar_max_height')
            + app_theme.widget('header_height')
            + app_theme.space('xl')
        )
        self.bind(scroll_locked=self._update_scroll)
        self.bind(width=self._recompute)
        self.bind(height=self._update_content_height)   # NOVO

    def _update_content_height(self, *args):             # NOVO
        """Gráfico ocupa toda a altura disponível do container — barras
        encostam (quase) na borda de baixo, em vez de ficar preso a um
        valor fixo do tema."""
        if self.height:
            self.content_height = self.height

            
    def _update_scroll(self, *args):
        self.do_scroll_x = not self.scroll_locked
        self.do_scroll_y = False

    def on_data_changed(self, *args):
        pass

    def _recompute(self, *args) -> None:
        """Coluna = % da tela quando cabe, mínimo do tema quando não cabe."""
        n = self._n_cols
        if not n or not self.width:
            return
        spacing = app_theme.space('md')
        min_col = app_theme.widget('bar_min_width')
        col_w = max(min_col, (self.width - spacing * (n - 1)) / n)
        self.cell_width = col_w
        self.content_width = n * col_w + (n - 1) * spacing


    def draw_self(
        self,
        data: SingleRowMatrixView,
        cell_factory: Callable[[int, dict], dict],
    ) -> None:
        
        logger.debug(f"headers únicos: {len(set(data.col_headers))} de {len(data.col_headers)} totais")

        max_gly = max(c["glycemia"] for c in data.cells)
        max_long = max(c["long_acting_insulin"] for c in data.cells)
        max_short = max(c["short_acting_insulin"] for c in data.cells)

        view_data = []
        for idx, header in enumerate(data.col_headers):
            cell_dict = cell_factory(idx, data.cells[idx])

            gly = cell_dict["glycemia_value"]
            long = cell_dict["long_value"]
            short = cell_dict["short_value"]

            cell_dict.update({
                "viewclass": "BarCell",
                "header_text": header,
                "glycemia_ratio": gly / max_gly if max_gly else 0,
                "long_ratio": long / max_long if max_long else 0,
                "short_ratio": short / max_short if max_short else 0,
            })
            view_data.append(cell_dict)

        self._n_cols = len(data.col_headers)
        self.layout_cols = self._n_cols
        self._recompute()

        self.data = view_data
        self.dispatch("on_data_changed")