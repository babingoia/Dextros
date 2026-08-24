# json_handler.py
from logging import getLogger
import json as js
from pathlib import Path
import json

from usecases.dtos.cardDTO import CardDTOInput


logger = getLogger(__name__)


class JsonHandler:
    def __init__(self, save_path):
        logger.debug(f"Initializing JsonHandler with save_path: {save_path}")

        self.save_path = save_path
        

    def save_to_json(self, data: list[CardDTOInput]) -> None:
        save_path = Path(self.save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        tmp_path = save_path.with_suffix(save_path.suffix + ".tmp")

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump({"cards": [self._serialize_card(card) for card in data]}, f, indent=2)

        tmp_path.replace(save_path)


    def load_from_json(self) -> list[CardDTOInput]:
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return [CardDTOInput(**card) for card in data.get("cards", [])]

        except FileNotFoundError:
            logger.debug("JSON file not found: %s. Returning empty list.", self.save_path)
            return []

        except json.JSONDecodeError:
            logger.exception("Invalid JSON found in %s", self.save_path)
            raise

        except (KeyError, TypeError):
            logger.exception("Invalid card data in %s", self.save_path)
            raise