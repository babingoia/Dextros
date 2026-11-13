from dataclasses import dataclass

from core.value_objects.food import Food


@dataclass
class FoodSearchResult:
    """Resultado de uma busca na tabela TACO: lista de Foods já ordenada por relevância."""
    foods: list[Food]
