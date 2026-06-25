# json_handler.py
from logging import getLogger

import json as js
from core.value_objects.card import Card


logger = getLogger(__name__)


class JsonHandler:
    def __init__(self, save_path=None):
        logger.debug(f"Initializing JsonHandler with save_path: {save_path}")

        self.save_path = save_path
        

    def save_to_json(self, data: list[Card]):
        logger.debug(f"Saving {len(data)} cards to JSON at: {self.save_path}")

        with open(self.save_path, "w") as f:
            js.dump({"cards": [card.to_dict() for card in data]}, f)


    def load_from_json(self) -> list[Card]:
        logger.debug(f"Loading cards from JSON at: {self.save_path}")
        
        try:
            with open(self.save_path, "r") as f:
                data = js.load(f)
            return [Card.from_dict(c) for c in data.get("cards", [])]
        except (FileNotFoundError, js.JSONDecodeError, KeyError, TypeError):
            return []