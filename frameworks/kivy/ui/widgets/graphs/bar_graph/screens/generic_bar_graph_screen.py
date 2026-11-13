from kivy.uix.accordion import ListProperty
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from logging import getLogger

from frameworks.kivy.ui.widgets.graphs.bar_graph.legend_item import LegendItem
from frameworks.kivy.ui.widgets.graphs.bar_graph.generic_bar_graph import GenericBarGraph

logger = getLogger(__name__)

Builder.load_file("frameworks/kivy/ui/widgets/graphs/bar_graph/screens/generic_bar_graph_screen.kv")


class BarGraphScreen(Screen):
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


class BarGraphScreenContent(BoxLayout):
    title = StringProperty("Gráfico")
    legend = ListProperty([])  # NOVO — [{"label": str, "color_name": str}, ...], injetado pelo controller

    graph = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._build, 0)

    def _build(self, dt) -> None:
        graph = GenericBarGraph()
        self.graph = graph
        self.ids.container.add_widget(graph)
        self._render_legend()                          # NOVO
        self.bind(legend=lambda *a: self._render_legend())  # NOVO
        logger.info(f"BarGraphScreenContent montou: '{self.title}'")

    def _render_legend(self):                            # NOVO
        holder = self.ids.legend_holder
        holder.clear_widgets()
        for item in self.legend:
            holder.add_widget(LegendItem(
                label_text=item.get("label", ""),
                color_name=item.get("color_name", "primary"),
            ))