"""Sticky como decorator do gráfico/célula.
- Constrói as faixas UMA vez (lazy); toggle = reparentar, não rebuildar.
- Sem properties de célula: lê tudo de cell_cls; scale injetado.
- O body É o próprio target; faixas se sincronizam pelo scroll."""
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from logging import getLogger

logger = getLogger(__name__)

Builder.load_string("""
<StickyInnerView@RecycleView>:
    RecycleGridLayout:
        default_size_hint: None, None
        size_hint: None, None
        width: self.minimum_width
        height: self.minimum_height
""")


class Sticky(EventDispatcher):
    enabled = BooleanProperty(False)
    scale = NumericProperty(1.0)  # injetado (a view binda do zoom)

    def __init__(self, target, cell_cls, **kwargs):
        super().__init__(**kwargs)
        self.target = target
        self.cell_cls = cell_cls
        self._host = None

        # Composto vivo entre toggles (nunca é destruído).
        self._composite = None
        self._corner = None
        self._top_view = self._top_layout = None
        self._left_view = self._left_layout = None
        self._top_row = self._bottom_row = None

        self.bind(enabled=self._on_enabled, scale=self._apply_metrics)
        self.target.fbind("data_changed", self.sync_headers)

    def toggle(self) -> None:
        self.enabled = not self.enabled

    def _on_enabled(self, *args) -> None:
        if self.enabled:
            self._mount()
        else:
            self._unmount()

    # ------------------------------------------------------------------
    # Construção única (lazy)
    # ------------------------------------------------------------------
    def _make_view(self, viewclass, cols=1):
        rv = Factory.get("StickyInnerView")()
        rv.viewclass = viewclass
        rv.do_scroll_x = False
        rv.do_scroll_y = False
        layout = rv.layout_manager or rv.children[0]
        layout.cols = cols
        return rv, layout

    def _build_composite(self) -> None:
        viewclass = self.cell_cls.__name__

        self._corner = self.cell_cls()
        for key, value in self.target.corner_dict().items():
            setattr(self._corner, key, value)
        self._corner.size_hint = (None, None)

        self._top_view, self._top_layout = self._make_view(viewclass, cols=1)
        self._left_view, self._left_layout = self._make_view(viewclass, cols=1)
        self._left_view.size_hint_x = None

        self._top_row = BoxLayout(orientation="horizontal")
        self._top_row.size_hint_y = None
        self._top_row.add_widget(self._corner)
        self._top_row.add_widget(self._top_view)

        self._bottom_row = BoxLayout(orientation="horizontal")
        self._bottom_row.add_widget(self._left_view)

        self._composite = BoxLayout(orientation="vertical")
        self._composite.add_widget(self._top_row)
        self._composite.add_widget(self._bottom_row)

        # Sync de scroll (faixas seguem o body). Bindado 1x, vive pra sempre.
        self.target.fbind("scroll_x", self._sync_x)
        self.target.fbind("scroll_y", self._sync_y)

    # ------------------------------------------------------------------
    # Toggle = reparentar
    # ------------------------------------------------------------------
    def _mount(self) -> None:
        host = self.target.parent or self._host
        if host is None:
            logger.warning("Sticky: target sem parent; adicione o gráfico antes de habilitar.")
            return
        self._host = host

        if self._composite is None:
            self._build_composite()
            self._apply_metrics()

        # Target sai de onde estiver e entra no composto.
        if self.target.parent is not None:
            self.target.parent.remove_widget(self.target)
        self._bottom_row.add_widget(self.target)

        # Composto entra no host.
        if self._composite.parent is not host:
            if self._composite.parent is not None:
                self._composite.parent.remove_widget(self._composite)
            host.add_widget(self._composite)

        self.target.headers_visible = False
        self.target.refresh()
        self.sync_headers()

        Clock.schedule_once(self._settle, 0)

    def _unmount(self) -> None:
        if self._composite is None:
            return

        # ⚠️ FIX DO WIPE: tira o target do composto ANTES de descartar o
        # composto, e devolve ele pro host INCONDICIONALMENTE.
        if self.target.parent is not None:
            self.target.parent.remove_widget(self.target)

        if self._composite.parent is not None:
            self._composite.parent.remove_widget(self._composite)

        if self._host is not None:
            self._host.add_widget(self.target)

        # Composto continua vivo (self._composite etc.), só fora da árvore.
        self.target.headers_visible = True
        self.target.refresh()

    # ------------------------------------------------------------------
    # Dados das faixas (barato: só referências do cache do target)
    # ------------------------------------------------------------------
    def sync_headers(self, *args) -> None:
        if self._top_view is None:
            return
        col_dicts, row_dicts = self.target.header_parts()
        self._top_layout.cols = max(len(col_dicts), 1)
        self._left_layout.cols = 1
        self._top_view.data = col_dicts
        self._left_view.data = row_dicts

    def _sync_x(self, inst, val) -> None:
        self._top_view.scroll_x = val

    def _sync_y(self, inst, val) -> None:
        self._left_view.scroll_y = val

    def _settle(self, dt) -> None:
        if self._composite is None or self._composite.parent is None:
            return
        self._apply_metrics()
        for rv in (self._top_view, self._left_view, self.target):
            rv.refresh_views()

    # ------------------------------------------------------------------
    # Métricas: célula é a fonte de verdade, scale é injetado.
    # ------------------------------------------------------------------
    def _apply_metrics(self, *args) -> None:
        if self._composite is None:
            return
        c = self.cell_cls
        w = c.base_width * self.scale
        h = c.base_height * self.scale
        sp = c.base_spacing * self.scale

        for layout in (self._top_layout, self._left_layout):
            layout.default_size = (w, h)
            layout.spacing = sp

        self._corner.width = w
        self._corner.height = h
        self._top_row.height = h
        self._top_row.spacing = sp
        self._bottom_row.spacing = sp
        self._left_view.width = w
        self._composite.spacing = sp