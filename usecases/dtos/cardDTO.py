from dataclasses import dataclass, InitVar, field


@dataclass
class _ExerciseDTO:
    exercise_name: str
    intensity: str

@dataclass()
class CardDTOInput:
    card_id: str
    card_date: str
    card_time: str
    glycemia: str
    long_acting_insulin: str
    short_acting_insulin: str
    meal: str
    observation: str

    exercise_name: InitVar[str]
    exercise_intensity: InitVar[str]

    exercise: _ExerciseDTO = field(init=False)

    def __post_init__(self, exercise_name: str, exercise_intensity: str):
        self.exercise = _ExerciseDTO(exercise_name, exercise_intensity)