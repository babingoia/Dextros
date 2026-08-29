from typing import TypedDict


class _Exercise(TypedDict):
    exercise_name: str
    intensity: str


class CardViewModel(TypedDict):
    card_id: str
    card_data: str
    card_time: str
    glycemia: str
    long_acting_insulin: str
    short_acting_insulin: str
    exercise: _Exercise
    meal: str
    observation: str