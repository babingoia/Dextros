from core.value_objects.meal import _VALID_MEAL_VALUES
from usecases.dtos.meal_list import MealList

class GetMealListUseCase:
    """Retorna uma cópia dos valores válidos de refeição."""
    def execute(self) -> MealList:
        return MealList(_VALID_MEAL_VALUES.copy()) 