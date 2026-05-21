from kivy.app import App
from View.Kivy.MainScene import MainScene
from kivymd.app import MDApp

class DextroApp(MDApp):
    def build(self):
        return MainScene()

DextroApp().run()