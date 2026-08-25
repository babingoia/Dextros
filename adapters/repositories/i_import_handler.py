from abc import ABC, abstractmethod
from adapters.DTOs.card_data_model import CardDataModel


class ICardImportHandler(ABC):

    save_path: str

    @abstractmethod
    def load(self) -> list[CardDataModel]: pass


    @abstractmethod
    def export(self, data: CardDataModel) -> None: pass