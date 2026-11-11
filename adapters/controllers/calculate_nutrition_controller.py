from logging import getLogger
from usecases.calculate_nutrition_use_case import CalculateNutritionUseCase
from core.value_objects.meal import Meal
from adapters.controllers.i_controller import IController

logger = getLogger(__name__)


class CalculateNutritionController(IController[dict, Meal | None]):
    """Query que converte (Food, gramas) em Meal consumido via rota,
    preservando o padrão rota -> controller -> use case do app inteiro.
    Recebe um dicionário com "food" e "grams"."""
    def __init__(self, calculate_nutrition_use_case: CalculateNutritionUseCase):
        self.calculate_nutrition_use_case = calculate_nutrition_use_case

    def execute(self, request: dict) -> Meal | None:
        logger.debug(f"Calculate nutrition request got: {request}")

        try:
            return self.calculate_nutrition_use_case.execute(
                food=request["food"],
                grams=request["grams"],
            )
        except KeyError as err:
            raise TypeError(f"Malformed calculate nutrition request, missing key: {err}") from err
