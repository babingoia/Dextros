import pytest

from hypothesis import strategies as st
from datetime import datetime
from tests.config.core.card_id import valid_card_id

from core.value_objects.card import Card
from core.value_objects.date import Date
from core.value_objects.exercise import Exercise, _INTENSITY_POSSIBLE_VALUES
from core.value_objects.glycemia import Glycemia
from core.value_objects.long_acting_insulin import LongActingInsulin
from core.value_objects.meal import MealPeriod, _VALID_MEAL_VALUES
from core.value_objects.observation import Observation
from core.value_objects.short_acting_insulin import ShortActingInsulin
from core.value_objects.time import Time


meal_possible_values = _VALID_MEAL_VALUES + [None]
intensity_possible_values = _INTENSITY_POSSIBLE_VALUES + [None]


@st.composite
def valid_date(draw) -> Date:
    generated_date = draw(st.dates(max_value=datetime.today().date()))
    new_date = Date.parse(generated_date)
    return new_date


@st.composite
def valid_time(draw) -> Time:
    generated_time = draw(st.times(max_value=datetime.today().time()))
    new_time = Time.parse(generated_time)
    return new_time


@st.composite
def valid_exercise(draw) -> Exercise:
    new_exercise = Exercise.parse(
        exercise_name=draw(st.text(max_size=64)),
        intensity=draw(st.sampled_from(intensity_possible_values))
    )
    return new_exercise


@st.composite
def valid_glycemia(draw) -> Glycemia:
    new_glycemia = Glycemia.parse(
        glycemia=draw(st.integers(min_value=0, max_value=600))
    )
    return new_glycemia


@st.composite
def valid_long_acting_insulin(draw) -> LongActingInsulin:
    return LongActingInsulin.parse(
        quantity=draw(st.integers(min_value=0))
    )


@st.composite
def valid_short_acting_insulin(draw) -> ShortActingInsulin:
    return ShortActingInsulin.parse(
        quantity=draw(st.integers(min_value=0))
    )


@st.composite
def valid_meal(draw) -> MealPeriod:
    new_value = MealPeriod.parse(draw(st.sampled_from(meal_possible_values.copy())))
    return new_value


@st.composite
def valid_observation(draw) -> Observation:
    new_obs = Observation.parse(draw(st.text(max_size=240)))
    return new_obs


@st.composite()
def valid_card(draw) -> Card:
    return Card(
        card_id=draw(valid_card_id()),
        card_date=draw(valid_date()),
        card_time=draw(valid_time()),
        glycemia=draw(valid_glycemia()),
        long_acting_insulin=draw(valid_long_acting_insulin()),
        short_acting_insulin=draw(valid_short_acting_insulin()),
        exercise=draw(valid_exercise()),
        meal=draw(valid_meal()),
        obs=draw(valid_observation())
    )


@st.composite
def valid_card_dto(draw) -> dict:
    pass