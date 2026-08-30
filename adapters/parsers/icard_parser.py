from abc import ABC, abstractmethod

from usecases.dtos.cardDTOInput import CardDTOInput
from adapters.repositories.DTOs.card_data_model import CardDataModel

class ICardParser(ABC):
    """Interface bastante inútil. Precisa ser substituida junto a sua implementação por função utilitária."""
    @abstractmethod
    def parse(self, data_model: CardDataModel) -> CardDTOInput: pass