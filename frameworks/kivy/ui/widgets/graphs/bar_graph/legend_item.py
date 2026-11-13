from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.factory import Factory
from kivy.lang import Builder

Builder.load_file("frameworks/kivy/ui/widgets/graphs/bar_graph/legend_item.kv")


class LegendItem(BoxLayout):
    """Par 'bolinha colorida + texto', usado na legenda do gráfico de barras."""
    label_text = StringProperty("")
    color_name = StringProperty("primary")


Factory.register("LegendItem", cls=LegendItem)