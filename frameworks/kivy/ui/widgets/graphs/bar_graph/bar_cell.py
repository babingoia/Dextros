from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from logging import getLogger

from frameworks.kivy.ui.widgets.popup.dialog import MetricsSummaryDialog

logger = getLogger(__name__)

Builder.load_file("frameworks/kivy/ui/widgets/graphs/bar_graph/bar_cell.kv")


class BarCell(FloatLayout):
    header_text = StringProperty("")

    glycemia_value = NumericProperty(0)
    glycemia_ratio = NumericProperty(0)
    glycemia_occurrences = NumericProperty(0)

    long_value = NumericProperty(0)
    long_ratio = NumericProperty(0)
    long_occurrences = NumericProperty(0)

    short_value = NumericProperty(0)
    short_ratio = NumericProperty(0)
    short_occurrences = NumericProperty(0)

    dialog_metrics = ListProperty([])

    def _show_details(self):
        logger.debug(f"Showing average details for: {self.header_text}")
        MetricsSummaryDialog(
            title=f"Detalhes: {self.header_text}",
            metrics=self.dialog_metrics,
        ).open()


Factory.register("BarCell", cls=BarCell)    