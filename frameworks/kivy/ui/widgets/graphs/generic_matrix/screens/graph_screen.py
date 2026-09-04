from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from logging import getLogger

from frameworks.kivy.ui.widgets.graphs.generic_matrix.generic_matrix_graph import GenericMatrixGraph
from frameworks.kivy.ui.widgets.graphs.generic_matrix.matrix_cell import MatrixCell
from frameworks.kivy.ui.widgets.graphs.generic_matrix.decorators.zoom_decorator import PinchZoom
from frameworks.kivy.ui.widgets.graphs.generic_matrix.decorators.sticky_decorator import Sticky
import frameworks.kivy.ui.widgets.graphs.generic_matrix.controls.zoom_controls 

logger = getLogger(__name__)

Builder.load_file("frameworks/kivy/ui/widgets/graphs/generic_matrix/screens/graph_screen.kv")

_STICKY_SESSION: dict[str, bool] = {}


class GraphScreen(Screen):
    def __init__(self, refresh_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.refresh_callback = refresh_callback

    def on_pre_enter(self, *args):
        logger.info(f"🔄 on_pre_enter DISPARADO para: {self.name}")
        super().on_pre_enter(*args)
        if self.refresh_callback:
            logger.info(f"⚡ Executando lazy load para: {self.name}")
            self.refresh_callback()
        else:
            logger.warning(f"⚠️ refresh_callback é None na tela {self.name}!")


class GraphScreenContent(BoxLayout):
    """A view. Constrói o renderer + os decorators e faz as ligações.
    O controller só usa .graph pra injetar dados."""

    title = StringProperty("")
    session_key = StringProperty("")

    graph = ObjectProperty(None, allownone=True)
    zoom = ObjectProperty(None, allownone=True)
    sticky = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._build, 0)

    def _build(self, dt) -> None:
        graph = GenericMatrixGraph()

        zoom = PinchZoom(target=graph)
        zoom.session_key = self.session_key

        sticky = Sticky(target=graph, cell_cls=MatrixCell)

        # Ligações: responsabilidade da view. Nenhum decorator conhece o outro.
        zoom.fbind('zoom_level', self._sync_scale)
        zoom.fbind('is_pinching', self._sync_lock)

        self.graph, self.zoom, self.sticky = graph, zoom, sticky
        self.ids.container.add_widget(graph)

        # Sessão do sticky + persistência
        if _STICKY_SESSION.get(self.session_key):
            sticky.enabled = True
        sticky.fbind('enabled', lambda *a: _STICKY_SESSION.update({self.session_key: sticky.enabled}))

        # Zoom só age na screen atual
        zoom.active = False
        screen = self._parent_screen()
        if screen is not None:
            screen.fbind("on_pre_enter", lambda *a: setattr(zoom, "active", True))
            screen.fbind("on_leave", lambda *a: setattr(zoom, "active", False))

        self._sync_scale()
        logger.info(f"GraphScreenContent montou: '{self.title}'")

    def _sync_scale(self, *args) -> None:
        self.graph.scale = self.zoom.zoom_level
        self.sticky.scale = self.zoom.zoom_level

    def _sync_lock(self, *args) -> None:
        self.graph.scroll_locked = self.zoom.is_pinching

    def _parent_screen(self):
        node = self.parent
        while node is not None:
            if isinstance(node, Screen):
                return node
            node = getattr(node, "parent", None)
        return None