from logging import getLogger


from utils.exceptions import DomainExceptionError
from usecases.IRepository import ICardRepository
from usecases.dtos.cardDTO import CardDTOInput
from core.value_objects.card import Card
from core.value_objects.card_id import CardID
from core.value_objects.date import Date
from core.value_objects.time import Time
from core.value_objects.glycemia import Glycemia
from core.value_objects.long_acting_insulin import LongActingInsulin
from core.value_objects.short_acting_insulin import ShortActingInsulin
from core.value_objects.exercise import Exercise
from core.value_objects.meal import MealPeriod
from core.value_objects.observation import Observation


logger = getLogger(__name__)


class CreateCardUseCase:
    
    def __init__(self, repository: ICardRepository):
        self.repository = repository


    def _create_card(self, cardDTO: CardDTOInput) -> Card:
        new_card_id = CardID.parse(cardDTO.card_id)
        new_card_date = Date.parse(cardDTO.date)
        new_card_time = Time.parse(cardDTO.time)
        new_card_glycemia = Glycemia.parse(cardDTO.glycemia)
        new_card_long_acting_insulin = LongActingInsulin.parse(cardDTO.long_acting_insulin)
        new_card_short_acting_insulin = ShortActingInsulin.parse(cardDTO.short_acting_insulin)
        new_card_exercise = Exercise.parse(cardDTO.exercise)
        new_card_meal = MealPeriod.parse(cardDTO.meal)
        new_card_obs = Observation.parse(cardDTO.obs)
            
        new_card = Card(new_card_id, new_card_date, new_card_time,
                        new_card_glycemia, new_card_long_acting_insulin, new_card_short_acting_insulin,
                        new_card_exercise, new_card_meal, new_card_obs)
        
        return new_card


    def execute(self, cardDTO: CardDTOInput) -> Card:
        """Cria um card a partir de um dicionário."""

        if cardDTO == None:
            logger.warning(f"CardDTO missing.")
            raise DomainExceptionError(f"Card creation failed, cardDTO is missing.")
        
        logger.debug(f"Creating Card from dto: {cardDTO}")

        new_card = self._create_card(cardDTO)    
        self.repository.add_card(new_card)
        return new_card
