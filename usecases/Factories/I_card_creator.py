from abc import ABC, abstractmethod

from usecases.dtos.cardDTOInput import CardDTOInput
from core.value_objects.card import Card

class ICardCreator(ABC):
    """Representa um cardCreator que recebe um CardDTOInput e transforma em card. 
    Deve ser removida para simplificação do projeto,
    """
    @abstractmethod
    def create_card(self, data: CardDTOInput) -> Card: pass