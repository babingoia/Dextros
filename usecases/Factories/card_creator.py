from datetime import datetime, timedelta
from logging import getLogger

from usecases.dtos.cardDTOInput import CardDTOInput
from usecases.Factories.I_card_creator import ICardCreator
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
from usecases.utils.exceptions import CardCreationError


logger = getLogger(__name__)


class CardCreator(ICardCreator):
    """Classe concreta que cria Cards á partir de um CardDTOInput."""
    def create_card(self, data: CardDTOInput) -> Card:
        try:
            new_card_id = CardID.parse(data.card_id)
            new_card_date = Date.parse(data.card_date)
            new_card_time = Time.parse(data.card_time)
            new_card_glycemia = Glycemia.parse(data.glycemia)
            new_card_long_acting_insulin = LongActingInsulin.parse(data.long_acting_insulin)
            new_card_short_acting_insulin = ShortActingInsulin.parse(data.short_acting_insulin)
            new_card_exercise = Exercise.parse(data.exercise.exercise_name, data.exercise.intensity)
            new_card_meal = MealPeriod.parse(data.meal)
            new_card_obs = Observation.parse(data.observation)
                
            new_card = Card(new_card_id, new_card_date, new_card_time,
                            new_card_glycemia, new_card_long_acting_insulin, new_card_short_acting_insulin,
                            new_card_exercise, new_card_meal, new_card_obs)
            
            return new_card
        except (ValueError, TypeError) as err:
            raise CardCreationError(err)