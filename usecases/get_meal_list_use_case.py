from core.value_objects.meal import _VALID_MEAL_VALUES
from usecases.dtos.meal_list import MealList

class GetMealListUseCase:
    def execute(self) -> MealList:
        return MealList(_VALID_MEAL_VALUES.copy()) 