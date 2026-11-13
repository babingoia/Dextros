"""Controller da rota search_food: valida o request e delega ao use case.

Mapeia a convenção de UI "todas" (spinner sem filtro) para None (sem filtro
de verdade no use case).
"""

from logging import getLogger
from usecases.search_food_use_case import SearchFoodUseCase
from usecases.dtos.food_search import FoodSearchResult
from adapters.controllers.i_controller import IController

logger = getLogger(__name__)

# Convenção de UI: o spinner de categorias usa "todas" como opção sem filtro.
_NO_CATEGORY_KEYWORD = "todas"


class SearchFoodController(IController[dict, FoodSearchResult]):
    """Query que busca alimentos na tabela TACO. Recebe um dicionário com
    "query" (obrigatório), "category" (opcional) e "limit" (opcional)."""
    def __init__(self, search_food_use_case: SearchFoodUseCase):
        self.search_food_use_case = search_food_use_case

    def execute(self, request: dict) -> FoodSearchResult:
        """Extrai "query" (obrigatório), "category" e "limit" do request e
        devolve o FoodSearchResult. Request sem "query" vira TypeError.
        """
        logger.debug(f"Search food request got: {request}")

        try:
            return self.search_food_use_case.execute(
                query=request["query"],
                category=request.get("category") if request.get("category") != _NO_CATEGORY_KEYWORD else None,
                limit=request.get("limit", SearchFoodUseCase.DEFAULT_LIMIT),
            )
        except KeyError as err:
            raise TypeError(f"Malformed search request, missing key: {err}") from err
