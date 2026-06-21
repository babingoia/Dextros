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


    def create_card(self, card_type: str, data: Card) -> Widget:
        new_widget = None

        if card_type == CARD:
            logger.debug(f"Creating card with data: {data.to_dict()}")
            new_widget = self._card(data)
        
        elif card_type == NONE_CARD:
            new_widget = self._none_card()
        
        if new_widget is not None:
            logger.debug(f"Card widget created successfully for type: {card_type}")
            return new_widget
        
        logger.warning(f"Card widget cannot be created for type: {card_type}")


    def alter_card(self):
        logger.debug("Alter card method called - currently not implemented.")


    def _card(self, data: Card) -> Widget:
        new_widget = Border(border_width=BORDER_WIDTH)
        btn = Button(
            text=str(data.dextro),
            size_hint=(None, None),
            size=(CELL_W, CELL_H),
        )
        btn.bind(on_press=lambda _inst, c=data: self._show_card_details(c))
        new_widget.add_widget(btn)
        return new_widget


    def _none_card(self) -> Widget:
        new_widget = Border(border_color=(1, 0, 0, 1), border_width=BORDER_WIDTH)
        new_widget.add_widget(Label(text="X", size_hint=(None, None), size=(CELL_W, CELL_H)))
        return new_widget


    def _show_card_details(self, card: Card) -> None:
        logger.debug(f"Showing details for card: {card}")
        
        content = CardWidget(card)

        width = min(dp(500), Window.width * 0.9)
        height = min(dp(450), Window.height * 0.9)

        popup = Popup(title="Card Details",
                     content=content, 
                     size_hint=(None, None),
                     size=(width, height)
                     )

        content.popup = popup
        popup.open()

