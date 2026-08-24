from abc import ABC, abstractmethod

from core.value_objects.card import Card

class ICardRepository(ABC):
    
    @abstractmethod
    def get_all_cards(self) -> list[Card]: pass

    @abstractmethod
    def get_card(self, card_id: str) -> Card: pass

    @abstractmethod
    def add_card(self, card: Card) -> None: pass

    @abstractmethod
    def remove_card(self, card_id: str) -> None: pass

    @abstractmethod
    def update_card(self, card: Card) -> None: pass