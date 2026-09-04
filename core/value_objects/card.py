from logging import getLogger
from dataclasses import dataclass
from datetime import datetime, date, timedelta

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
        # 1. Valida a intenção original do usuário (presente/passado)
        if self.card_date._date > date.today():
            raise ValueError(f"Card não pode ter data no futuro: {self.card_date._date}")

        # 2. Aplica a distorção/arredondamento de domínio
        dt = datetime.combine(self.card_date._date, self.card_time._time)
        if dt.minute >= 30:
            dt += timedelta(hours=1)
        dt = dt.replace(minute=0, second=0, microsecond=0)

        # 3. Atualiza os Value Objects com o horário arredondado
        object.__setattr__(self, "card_date", Date.parse(dt.date()))
        object.__setattr__(self, "card_time", Time.parse(dt.time()))
