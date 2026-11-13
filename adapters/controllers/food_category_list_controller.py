"""Controller da rota get_food_category_list: categorias da TACO para o spinner.

Query sem request (padrão do app para listas de referência, como GetTimeList).
"""

from logging import getLogger
from usecases.get_food_category_list_use_case import GetFoodCategoryListUseCase
from usecases.dtos.food_category_list import FoodCategoryList
from adapters.controllers.i_controller import IController

logger = getLogger(__name__)


class FoodCategoryListController(IController[None, FoodCategoryList]):
    """Query que retorna as categorias de alimentos da tabela TACO para o spinner da UI."""
    def __init__(self, food_category_list_use_case: GetFoodCategoryListUseCase):
        self.food_category_list_use_case = food_category_list_use_case

    def execute(self, request=None) -> FoodCategoryList:
        """Retorna a lista de categorias em ordem alfabética; request é ignorado."""
        logger.debug("Food category list request got")
        return self.food_category_list_use_case.execute()
