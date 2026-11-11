from dataclasses import dataclass


@dataclass
class FoodCategoryList:
    """Lista de categorias de alimentos disponíveis na tabela TACO."""
    category_values: list[str]
