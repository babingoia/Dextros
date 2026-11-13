"""Factory concreta de Card: monta o agregado de VOs a partir do CardDTOInput.

É AQUI, na fronteira do domínio, que a nutrição consumida (Meal) nasce e entra
aninhada no MealPeriod — a UI e os DTOs continuam planos e nunca manipulam o
dict aninhado. Qualquer VO inválido vira CardCreationError.
"""

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
from core.value_objects.meal import Meal, MealPeriod
from core.value_objects.observation import Observation
from usecases.utils.exceptions import CardCreationError


logger = getLogger(__name__)


class CardCreator(ICardCreator):
    """Classe concreta que cria Cards á partir de um CardDTOInput."""
    def create_card(self, data: CardDTOInput) -> Card:
        """Faz o parse de cada campo do DTO no seu VO e devolve o Card montado.
        A nutrição (Meal.parse) é composta dentro do MealPeriod.parse neste
        ponto único; levanta CardCreationError se qualquer VO rejeitar o dado.
        """
        try:
            new_card_id = CardID.parse(data.card_id)
            new_card_date = Date.parse(data.card_date)
            new_card_time = Time.parse(data.card_time)
            new_card_glycemia = Glycemia.parse(data.glycemia)
            new_card_long_acting_insulin = LongActingInsulin.parse(data.long_acting_insulin)
            new_card_short_acting_insulin = ShortActingInsulin.parse(data.short_acting_insulin)
            new_card_exercise = Exercise.parse(data.exercise.exercise_name, data.exercise.intensity)

            # Composição: a nutrição consumida (Meal) nasce aqui, na fronteira do
            # domínio, e entra dentro do MealPeriod — a UI nunca manipula o dict aninhado.
            new_card_meal_nutrition = Meal.parse(data.carbohydrate_g, data.fat_g)
            new_card_meal = MealPeriod.parse(data.meal, new_card_meal_nutrition)

            new_card_obs = Observation.parse(data.observation)

            new_card = Card(new_card_id, new_card_date, new_card_time,
                            new_card_glycemia, new_card_long_acting_insulin, new_card_short_acting_insulin,
                            new_card_exercise, new_card_meal, new_card_obs)

            return new_card
        except (ValueError, TypeError) as err:
            raise CardCreationError(err)
