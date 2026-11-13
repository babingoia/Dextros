"""Use case de listagem das categorias de alimentos presentes na tabela TACO.

Espelho direto do GetMealListUseCase: use case puro sobre dados de referência
injetados, sem repositório e sem porta nova.
"""

from logging import getLogger

from core.value_objects.food import Food
from usecases.dtos.food_category_list import FoodCategoryList

logger = getLogger(__name__)


class GetFoodCategoryListUseCase:
    """Retorna as categorias de alimentos presentes na tabela injetada.

    Espelho direto do GetMealListUseCase: use case puro sobre dados de referência,
    sem repositório. As categorias voltam cruas (com acento) para a UI exibir,
    e em ordem alfabética para o spinner ficar previsível.
    """

    def __init__(self, foods: list[Food]):
        self._categories = sorted({food.category for food in foods})

    def execute(self) -> FoodCategoryList:
        """Retorna as categorias cruas (com acento) e em ordem alfabética para
        o spinner da UI ficar previsível.
        """
        logger.debug(f"Food categories available: {len(self._categories)}")
        return FoodCategoryList(self._categories.copy())
