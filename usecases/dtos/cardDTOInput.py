from dataclasses import dataclass, InitVar, field


@dataclass
class _ExerciseDTO:
    exercise_name: str
    intensity: str

@dataclass()
class CardDTOInput:
    """DTO dataclass fortemente tipada que entra nos usecases."""
    card_id: int | str | None
    card_date: str
    card_time: str
    glycemia: int
    long_acting_insulin: int | None
    short_acting_insulin: int | None
    meal: str | None
    observation: str | None

    exercise_name: InitVar[str | None]
    exercise_intensity: InitVar[str | None]

    exercise: _ExerciseDTO = field(init=False)

    def __post_init__(self, exercise_name: str | None=None, exercise_intensity: str | None=None):
        self.exercise = _ExerciseDTO(exercise_name, exercise_intensity)