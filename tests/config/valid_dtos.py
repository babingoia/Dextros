import pytest

from hypothesis import given, strategies as st 

from .valid_objects import valid_card

from core.value_objects.card import Card
from usecases.dtos.cardDTOInput import CardDTOInput


@st.composite
def valid_card_dto_input(draw) -> CardDTOInput:
    values: Card = draw(valid_card())
    
    return CardDTOInput(
        card_id=values.card_id.card_id,
        card_date=values.card_date._date,
        card_time=values.card_time._time,
        glycemia=values.glycemia.glycemia,
        short_acting_insulin=values.short_acting_insulin.quantity,
        long_acting_insulin=values.long_acting_insulin.quantity,
        meal=values.meal.meal_period,
        exercise_intensity=values.exercise.intensity,
        exercise_name=values.exercise.exercise_name,
        observation=values.obs.observation
    )