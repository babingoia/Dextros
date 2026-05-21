from presentation.kivy.ui.MainScene import MainScene
from kivymd.app import MDApp

class DextroApp(MDApp):
    def build(self):
        return MainScene()

DextroApp().run()