# json_handler.py
import json as js
from core.value_objects.Card import Card


class JsonHandler:
    def __init__(self, save_path):
        self.save_path = save_path
        

    def save_to_json(self, data: list[Card]):
        with open(self.save_path, "w") as f:
            js.dump({"cards": [card.to_dict() for card in data]}, f)


    def load_from_json(self) -> list[Card]:
        try:
            with open(self.save_path, "r") as f:
                data = js.load(f)
            return [Card.from_dict(c) for c in data.get("cards", [])]
        except (FileNotFoundError, js.JSONDecodeError, KeyError, TypeError):
            return []