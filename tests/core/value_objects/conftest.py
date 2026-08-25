import pytest

from core.value_objects.card_id import CardID
from core.value_objects.date import Date
from core.value_objects.time import Time
from core.value_objects.glycemia import Glycemia
from core.value_objects.long_acting_insulin import LongActingInsulin
from core.value_objects.short_acting_insulin import ShortActingInsulin
from core.value_objects.exercise import Exercise
from core.value_objects.meal import MealPeriod
from core.value_objects.observation import Observation
from core.value_objects.card import Card


def make_card(**overrides) -> Card:
    """Fábrica de Card válido, com todos os campos usando valores padrão
    sensatos. Passe overrides pra sobrescrever campos específicos no teste."""
    defaults = dict(
        card_id=CardID.parse(),
        card_date=Date.parse("2024-05-20"),
        card_time=Time.parse("08:00"),
        glycemia=Glycemia.parse(100),
        long_acting_insulin=LongActingInsulin.parse(10),
        short_acting_insulin=ShortActingInsulin.parse(4),
        exercise=Exercise.parse(),
        meal=MealPeriod.parse("jejum"),
        obs=Observation.parse(),
    )
    defaults.update(overrides)
    return Card(**defaults)


@pytest.fixture
def valid_card_kwargs():
    return dict(
        card_id=CardID.parse(),
        card_date=Date.parse("2024-05-20"),
        card_time=Time.parse("08:00"),
        glycemia=Glycemia.parse(100),
        long_acting_insulin=LongActingInsulin.parse(10),
        short_acting_insulin=ShortActingInsulin.parse(4),
        exercise=Exercise.parse(),
        meal=MealPeriod.parse("jejum"),
        obs=Observation.parse(),
    )
