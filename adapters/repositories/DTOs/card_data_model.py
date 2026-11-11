from typing import TypedDict


class _ExerciseDataModel(TypedDict):

    exercise_name: str
    intensity: str


class _NutritionDataModel(TypedDict):
    """Valores nutricionais consumidos, em gramas inteiras. Espelho do VO Meal."""

    carbohydrate_g: int | None
    fat_g: int | None


class _MealDataModel(TypedDict):
    """Espelho do VO MealPeriod: período da refeição + nutrição opcional aninhada.

    Formato canônico no banco a partir da branch meal-improvements-for-real-food.
    Cards legados salvam meal como string — a leitura é retrocompatível no parser
    e a normalização do arquivo é responsabilidade do DatabaseMigrationService.
    """

    meal_period: str | None
    meal: _NutritionDataModel | None


class CardDataModel(TypedDict):
    """DTO em forma de dicionário tipado que cruza a fronteira banco <-> repositório."""
    card_id: str
    card_date: str
    card_time: str
    glycemia: int
    long_acting_insulin: int
    short_acting_insulin: int
    exercise: _ExerciseDataModel
    meal: _MealDataModel
    observation: str
