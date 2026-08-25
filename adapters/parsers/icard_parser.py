from abc import ABC, abstractmethod

from usecases.dtos.cardDTO import CardDTOInput
from adapters.DTOs.card_data_model import CardDataModel

class ICardParser(ABC):

    @abstractmethod
    def parse(self, data_model: CardDataModel) -> CardDTOInput: pass