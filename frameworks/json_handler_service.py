import json
import logging
from pathlib import Path
from typing import Iterable


from adapters.repositories.i_import_handler import ICardImportHandler
from adapters.DTOs.card_data_model import CardDataModel


logger = logging.getLogger(__name__)


class JsonHandler(ICardImportHandler):
    def __init__(self, save_path: str | Path):
        logger.debug(f"Initializing JsonHandler with save_path: {save_path}")
        self.save_path = Path(save_path)

    def export(self, data: Iterable[CardDataModel]) -> None:
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.save_path.with_suffix(self.save_path.suffix + ".tmp")

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump({"cards": list(data)}, f, indent=2, ensure_ascii=False)

        tmp_path.replace(self.save_path)

    def load(self) -> list[CardDataModel]:
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return [CardDataModel(card) for card in data.get("cards", [])]

        except FileNotFoundError:
            logger.debug("JSON file not found: %s. Returning empty list.", self.save_path)
            return []

        except json.JSONDecodeError:
            logger.exception("Invalid JSON found in %s", self.save_path)
            raise

        except (KeyError, TypeError, ValueError) as e:
            logger.exception("Invalid card data in %s: %s", self.save_path, e)
            raise