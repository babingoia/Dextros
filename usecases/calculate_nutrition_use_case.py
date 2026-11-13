"""Use case de cálculo de nutrição consumida: converte (Food, gramas) em Meal.

Wrapper de Meal.from_food mantido como use case para preservar o padrão rota
-> controller -> use case que o app segue inteiro, inclusive para cálculos
puros. Toda a regra de conversão vive no VO (core).
"""

from logging import getLogger

from core.value_objects.food import Food
from core.value_objects.meal import Meal

logger = getLogger(__name__)


class CalculateNutritionUseCase:
    """Converte (Food, gramas consumidas) em um Meal com os valores consumidos.

    Wrapper de Meal.from_food mantido como use case para preservar o padrão
    rota -> controller -> use case que o app segue inteiro, inclusive para
    cálculos puros. Toda a regra de conversão vive no VO (core); aqui não
    existe lógica além do repasse.
    """

    def execute(self, food: Food, grams) -> Meal | None:
        """Retorna o Meal consumido para a quantidade informada, ou None quando
        o alimento não tem nenhum dos dois nutrientes na tabela.
        """
        # from_food valida tipos antes de qualquer acesso aos atributos do food
        result = Meal.from_food(food, grams)
        logger.debug(f"Nutrition calculated for '{food.description}': {result}")
        return result
