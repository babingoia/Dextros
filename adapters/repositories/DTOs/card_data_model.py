from typing import TypedDict


class _ExerciseDataModel(TypedDict):

    exercise_name: str
    intensity: str


class CardDataModel(TypedDict):

    card_id: str
    card_date: str
    card_time: str
    glycemia: int
    long_acting_insulin: int
    short_acting_insulin: int
    exercise: _ExerciseDataModel
    meal: str
    observation: str