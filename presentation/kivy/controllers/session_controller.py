"""Controla o cache de cartões na sessão, garantindo que as alterações
    sejam refletidas em toda a aplicação."""
from __future__ import annotations
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.value_objects.card import Card


logger = getLogger(__name__)


class SessionController:
    _instance = None

    def __new__(cls, json_handler=None):
        if cls._instance is None:
            logger.info("Criando nova instância de SessionCache...")

            cls._instance = super().__new__(cls)
            cls._instance.cards_on_session = None
            cls._instance._listeners = {"on_add": [], "on_remove": []}
            cls._instance.json_handler = None
        
        if json_handler is not None:
            logger.info("Atribuindo JsonHandler à instância de SessionCache...")
            cls._instance.json_handler = json_handler
        
        logger.debug(f"Returning: SessionCache instância: {cls._instance}, JsonHandler: {cls._instance.json_handler}")
        return cls._instance
    

    @property
    def cards_on_session(self):
        logger.debug(f"Acessando cards_on_session...")

        if self._cards is None:
            self._cards = self.json_handler.load_from_json()
        return self._cards
    

    @cards_on_session.setter
    def cards_on_session(self, value):
        logger.debug(f"Atualizando cards_on_session: {value}")

        self._cards = value


    def add_card(self, card):
        logger.debug(f"Adicionando card: {card}")

        self.cards_on_session.append(card)
        self.json_handler.save_to_json(self.cards_on_session)
        self._emit("on_add")
    

    def remove_card(self, card):
        logger.debug(f"Removendo card: {card}")

        self.cards_on_session = [c for c in self.cards_on_session if not (c.data == card.data and c.horario == card.horario)]
        self.json_handler.save_to_json(self.cards_on_session)
        self._emit("on_remove")


    def get_cards(self) -> list[Card]:
        logger.debug("Obtendo cards da sessão")

        return self.cards_on_session
    

    def bind(self, event_name, callback):
        logger.debug(f"Registrando callback para evento '{event_name}'")

        if event_name in self._listeners:
            self._listeners[event_name].append(callback)
        else:
            raise ValueError(f"Evento '{event_name}' não suportado.")
    

    def _emit(self, event_name):
        logger.debug(f"Emitindo evento '{event_name}' para {len(self._listeners.get(event_name, []))} listeners")

        for callback in self._listeners[event_name]:
            callback()