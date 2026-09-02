"""Toolbar de zoom/sticky. Widgets independentes:
só conhecem os decorators injetados (zoom e sticky), nunca o gráfico."""
from kivy.factory import Factory
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder


class ToolButton(Button):
    """Botão utilitário temático com estado ativo (usado no 📌)."""
    active_state = BooleanProperty(False)


class ZoomControls(BoxLayout):
    """Barra - / 100% / + / 📌. Recebe os decorators por injeção
    (a view/screen faz o wiring: controls.zoom = zoom; controls.sticky = sticky)."""
    zoom = ObjectProperty(None, allownone=True)
    sticky = ObjectProperty(None, allownone=True)


Factory.register("ToolButton", cls=ToolButton)
Factory.register("ZoomControls", cls=ZoomControls)
Builder.load_file("frameworks/kivy/ui/widgets/graphs/controls/zoom_controls.kv")