# json_handler.py
import json as js
from core.value_objects.Card import Card

def get_save_path():
    from kivy.app import App
    app = App.get_running_app()
    if app is None:
        raise RuntimeError("get_save_path() chamado antes do app inicializar.")
    return app.user_data_dir + "/cards.json"

class JsonHandler:
    @staticmethod
    def save_to_json(data: list[Card], filename=None):
        filename = filename or get_save_path()   
        with open(filename, "w") as f:
            js.dump({"cards": [card.to_dict() for card in data]}, f)

    @staticmethod
    def load_from_json(filename=None) -> list[Card]:
        filename = filename or get_save_path()
        try:
            with open(filename, "r") as f:
                data = js.load(f)
            return [Card.from_dict(c) for c in data.get("cards", [])]
        except (FileNotFoundError, js.JSONDecodeError, KeyError, TypeError):
            return []