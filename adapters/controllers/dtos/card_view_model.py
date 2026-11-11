from typing import TypedDict


class _Exercise(TypedDict):
    exercise_name: str
    intensity: str


class CardViewModel(TypedDict):
    """DTO de fronteira em forma de dicionário tipado entre os controllers e a UI.
    Os campos de nutrição chegam como texto cru do formulário (podem conter vírgula
    decimal) — a normalização é responsabilidade do mapper, não da UI."""
    card_id: str
    card_data: str
    card_time: str
    glycemia: str
    long_acting_insulin: str
    short_acting_insulin: str
    exercise: _Exercise
    meal: str
    carbohydrate_g: str
    fat_g: str
    observation: str
