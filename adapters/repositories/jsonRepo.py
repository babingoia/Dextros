from logging import getLogger

from usecases.IRepository import ICardRepository
from core.value_objects.card import Card
from adapters.repositories.i_import_handler import ICardImportHandler
from usecases.Factories.I_card_creator import ICardCreator
from usecases.dtos.cardDTOInput import CardDTOInput
from adapters.parsers.icard_parser import ICardParser
from adapters.exceptions import CardNotFoundError
from adapters.repositories.DTOs.card_data_model import CardDataModel

logger = getLogger(__name__)


class JsonRepository(ICardRepository):
    """Classe concreta de repositório que utiliza loads e exports de um CardImportHandler como banco
    de dados. Precisa receber um card_creator para manipular e validar os dados além de um parser para
    mapear CardDataModel em CardDTOInput. Suporta operações basícas de um repositório.
    """

    def __init__(self, handler: ICardImportHandler, card_creator: ICardCreator, parser: ICardParser):
        
        self.parser: ICardParser = parser
        self.handler: ICardImportHandler = handler
        self.card_creator: ICardCreator = card_creator
        self.cards_on_session: list[Card] = self._import_cards()


    def _import_cards(self) -> list[Card]:
        logger.debug("Importing cards to repository...")
        data = self.handler.load()
        
        parsed_data: list[CardDTOInput] = []
        
        for data_model in data:
            parsed_data_model = self.parser.parse(data_model)
            parsed_data.append(parsed_data_model)
        
        cards: list[Card] = []

        for card in parsed_data:
            cards.append(self.card_creator.create_card(card))
        
        return cards


    def _map_card_to_data_model(self) -> list[CardDataModel]:
        
        parsed_cards_on_session: list[CardDataModel] = []
        
        for card in self.cards_on_session:
            parsed_card = CardDataModel(
                card_id=str(card.card_id.card_id), 
                card_date=card.card_date._date.isoformat(), 
                card_time=card.card_time._time.strftime("%H:%M"), 
                glycemia=card.glycemia.glycemia,
                long_acting_insulin=card.long_acting_insulin.quantity,
                short_acting_insulin=card.short_acting_insulin.quantity,
                meal=card.meal.meal_period,
                observation=card.obs.observation,
                exercise={
                    'exercise_name': card.exercise.exercise_name,
                    'intensity': card.exercise.intensity
                }
            )
            parsed_cards_on_session.append(parsed_card)

        return parsed_cards_on_session


    def get_all_cards(self) -> list[Card]:
        return list(self.cards_on_session)

    
    def get_card(self, card_id: str) -> Card:
        logger.debug(f"Seeking for card: {card_id}") 
        for card in self.cards_on_session:
            if card.card_id == card_id:
                return card
        
        raise CardNotFoundError(f"Card not found when searching for: {card_id}")

    
    def add_card(self, card: Card) -> None:
        logger.debug(f"Saving {card} to JSON...")
        
        self.cards_on_session.append(card)
        self.handler.export(self._map_card_to_data_model())


    def remove_card(self, card_id: str) -> None:
        logger.debug(f"Removing card with ID: {card_id}")

        for card in self.cards_on_session:
            if card.card_id == card_id:
                self.cards_on_session.remove(card)
                self.handler.export(self._map_card_to_data_model())
                return
        
        raise CardNotFoundError(f"Card not found when removing {card_id}")
        

    def update_card(self, card: Card) -> None:
        logger.debug(f"Updating card: {card} with id: {card.card_id.card_id}")
        for old_card in self.cards_on_session:
            if old_card.card_id == card.card_id:
                self.cards_on_session.remove(old_card)
                self.cards_on_session.append(card)
                self.handler.export(self._map_card_to_data_model())
                return
        
        raise CardNotFoundError(f"Card not found when updating: {card.card_id.card_id}")