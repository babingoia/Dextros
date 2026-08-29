from abc import ABC, abstractmethod

from usecases.dtos.cardDTOInput import CardDTOInput
from adapters.repositories.DTOs.card_data_model import CardDataModel

class ICardParser(ABC):

    @abstractmethod
    def parse(self, data_model: CardDataModel) -> CardDTOInput: pass