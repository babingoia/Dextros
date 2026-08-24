from logging import getLogger

from usecases.IRepository import ICardRepository
from infrastructure.json_handler_service import JsonHandler
from usecases.dtos.cardDTO import CardDTOInput


logger = getLogger(__name__)


class JsonRepository(ICardRepository):

    def __init__(self, save_path, handler=None):
        if handler is None:
            self.handler = JsonHandler(save_path)
        else:
            self.handler = handler

        self.cards_on_session: list[CardDTOInput] = self.handler.load_from_json()


    def get_all_cards(self) -> list[CardDTOInput]:
        logger.debug(f"Loading cards from JSON at: {self.save_path}")
        return list(self.cards_on_session)

    
    def get_card(self, card_id: str) -> CardDTOInput:
        logger.debug(f"Seeking for card: {id}") 
        for card in self.cards_on_session:
            if card.id == card_id:
                return card

    
    def add_card(self, card: CardDTOInput) -> None:
        logger.debug(f"Saving {card} to JSON at: {self.save_path}")
        
        self.cards_on_session.append(card)
        self.handler.save_to_json(self.cards_on_session)


    def remove_card(self, card_id: str) -> None:
        logger.debug(f"Removing card with ID: {id}")

        for card in self.cards_on_session:
            if card.id == card_id:
                self.cards_on_session.remove(card)
                self.handler.save_to_json(self.cards_on_session)
                break
        

    def update_card(self, card: CardDTOInput) -> None:
        logger.debug(f"Updating card: {card} with id: {card.id}")
        for old_card in self.cards_on_session:
            if old_card.id == card.id:
                self.cards_on_session.remove(old_card)
                self.cards_on_session.append(card)
                self.handler.save_to_json(self.cards_on_session)