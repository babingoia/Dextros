import pytest

from hypothesis import given, strategies as st
from datetime import datetime


from core.value_objects.card import Card
from core.value_objects.card_id import CardID
from core.value_objects.date import Date
from core.value_objects.exercise import Exercise, _INTENSITY_POSSIBLE_VALUES
from core.value_objects.glycemia import Glycemia
from core.value_objects.long_acting_insulin import LongActingInsulin
from core.value_objects.meal import MealPeriod, _VALID_MEAL_VALUES
from core.value_objects.observation import Observation
from core.value_objects.short_acting_insulin import ShortActingInsulin
from core.value_objects.time import Time


meal_possible_values = _VALID_MEAL_VALUES + [None]


@st.composite
def valid_card_id(draw) -> CardID:
    return CardID.parse()


@st.composite
def valid_date(draw) -> Date:
    generated_date = draw(st.dates(max_value=datetime.today().date()))
    new_date = Date(generated_date)
    return new_date


@st.composite
def valid_time(draw) -> Time:
    generated_time = draw(st.times(max_value=datetime.today().time()))
    new_time = Time(generated_time)
    return new_time


@st.composite
def valid_exercise(draw) -> Exercise:
    pass


@st.composite
def valid_glycemia(draw) -> Glycemia:
    pass


@st.composite
def valid_long_acting_insulin(draw) -> LongActingInsulin:
    pass


@st.composite
def valid_short_acting_insulin(draw) -> ShortActingInsulin:
    pass


@st.composite
def valid_meal(draw) -> MealPeriod:
    new_value = MealPeriod(draw(st.sampled_from(meal_possible_values.copy())))
    return new_value


@st.composite
def valid_observation(draw) -> Observation:
    pass


@st.composite
def valid_card(draw, *args) -> Card:
    pass