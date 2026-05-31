"""Controla o cache de cartões na sessão, garantindo que as alterações
    sejam refletidas em toda a aplicação."""
from __future__ import annotations
from infrastructure.json_handler import JsonHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.value_objects.Card import Card


class SessionCache:
    _instance = None

    def __new__(cls, json_handler=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cards_on_session = None
            cls._instance._listeners = {"on_add": [], "on_remove": []}
            cls._instance.json_handler = None
        
        if json_handler is not None:
            cls._instance.json_handler = json_handler
        
        return cls._instance
    

    @property
    def cards_on_session(self):
        if self._cards is None:
            self._cards = self.json_handler.load_from_json()
        return self._cards
    

    @cards_on_session.setter
    def cards_on_session(self, value):
        self._cards = value


    def add_card(self, card):
        self.cards_on_session.append(card)
        self.json_handler.save_to_json(self.cards_on_session)
        self._emit("on_add")
    

    def remove_card(self, card):
        self.cards_on_session = [c for c in self.cards_on_session if not (c.data == card.data and c.horario == card.horario)]
        self.json_handler.save_to_json(self.cards_on_session)
        self._emit("on_remove")


    def get_cards(self) -> list[Card]:
        return self.cards_on_session
    

    def bind(self, event_name, callback):
        if event_name in self._listeners:
            self._listeners[event_name].append(callback)
        else:
            raise ValueError(f"Evento '{event_name}' não suportado.")
    

    def _emit(self, event_name):
        print("Emitindo sinal...", event_name)
        for callback in self._listeners[event_name]:
            callback()