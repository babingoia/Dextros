from abc import ABC, abstractmethod
from adapters.repositories.DTOs.card_data_model import CardDataModel


class ICardImportHandler(ABC):
    """Interface para implementação de exporters e importers. Retorna ou salva uma lista
    de CardDataModel
    """

    save_path: str

    @abstractmethod
    # Load foi escolhido para não dar conflito com o import do python.
    def load(self) -> list[CardDataModel]: pass
    

    @abstractmethod
    def export(self, data: list[CardDataModel]) -> None: pass