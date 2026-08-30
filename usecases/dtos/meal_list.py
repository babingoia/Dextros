from dataclasses import dataclass


@dataclass
class MealList:
    """
    Representa uma lista de valores possíveis dentro do sistema de refeições.
    """
    meal_values: list[str]