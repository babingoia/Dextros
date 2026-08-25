from logging import getLogger
from dataclasses import dataclass
from datetime import date

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


@dataclass(frozen=True)
class Card:
    
    card_id: CardID
    card_date: Date
    card_time: Time
    glycemia: Glycemia
    long_acting_insulin: LongActingInsulin
    short_acting_insulin: ShortActingInsulin
    exercise: Exercise
    meal: MealPeriod
    obs: Observation

    def __post_init__(self):
        if self.card_date._date > date.today():
            raise ValueError(f"Card não pode ter data no futuro: {self.card_date._date}")
