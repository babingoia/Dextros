from abc import ABC, abstractmethod

from core.value_objects.card import Card

class ICardRepository(ABC):
    """
    Interface repository que define operações simples de banco de dados. Trabalha sempre com Cards já feitos
    e portanto já validados.
    """
    
    @abstractmethod
    def get_all_cards(self) -> list[Card]: 
        """Retorna uma lista de todos os Cards."""
        pass

    @abstractmethod
    def get_card(self, card_id: str) -> Card: 
        """Retorna um único Card pego por ID."""
        pass

    @abstractmethod
    def add_card(self, card: Card) -> None: 
        """Adiciona um card novo ao banco."""
        pass

    @abstractmethod
    def remove_card(self, card_id: str) -> None: 
        """Remove um card por sua ID."""
        pass

    @abstractmethod
    def update_card(self, card: Card) -> None:
        """Recebe um Card atualizado e deleta um outro de mesma ID para salvar o novo."""
        pass