from kivymd.app import MDApp
from os import path 

from infrastructure.json_handler import JsonHandler
from presentation.kivy.controllers.main_controller import MainController
from presentation.kivy.controllers.SessionCache import SessionCache


class DextroApp(MDApp):
    def build(self):
        save_path = path.join(self.user_data_dir, "cards.json")
        print(save_path)
        handler = JsonHandler(save_path=save_path)
        print(handler)
        cache = SessionCache(json_handler=handler)
        print(cache, cache.json_handler)
        self.controller = MainController()
        return self.controller.main_view


DextroApp().run()