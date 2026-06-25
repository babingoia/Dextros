"""Classe que gerencia a criação de cards"""
from __future__ import annotations

from kivy.uix.actionbar import Label
from kivy.uix.accordion import Widget
from typing import TYPE_CHECKING    
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core.window import Window
from logging import getLogger


from presentation.kivy.ui.widgets.loader import Border
from presentation.kivy.ui.configs import CELL_H, CELL_W, BORDER_WIDTH
from presentation.kivy.ui.widgets.loader import CardWidget


if TYPE_CHECKING:
    from core.value_objects.card import Card


NONE_CARD = "none_card"
CARD = "card"
logger = getLogger(__name__)


class CardCreator():
    def __init__(self):
        logger.info("CardCreator initialized")


    def create_card(self, card_type: str, data: Card) -> dict:
        template = None

        if card_type == CARD:
            logger.debug(f"Creating card with data: {data.to_dict()}")
            template = self._card(data)
        
        elif card_type == NONE_CARD:
            template = self._none_card()
        
        if template is not None:
            logger.debug(f"Card widget created successfully for type: {card_type} with data: {template}")
            return template
        
        logger.warning(f"Card widget cannot be created for type: {card_type}")


    def _card(self, data: Card) -> dict:
        return {
            "is_empty": False,
            "is_header": False,
            "dextro_text": data.dextro,
            "card_reference": data
        }


    def _none_card(self) -> dict:
        return {
            "is_empty": True,
            "is_header": False,
            "dextro_text": "x",
            "card_reference": None
        }
