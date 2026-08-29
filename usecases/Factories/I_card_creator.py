from abc import ABC, abstractmethod

from usecases.dtos.cardDTOInput import CardDTOInput
from core.value_objects.card import Card

class ICardCreator(ABC):

    @abstractmethod
    def create_card(self, data: CardDTOInput) -> Card: pass