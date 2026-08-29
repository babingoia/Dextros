from typing import Any

from usecases.dtos.meal_list import MealList
from adapters.controllers.i_controller import IController



class MealController(IController[Any, MealList]):
    def __init__(self, get_meal_list_use_case):
        self.get_meal_list_use_case = get_meal_list_use_case


    def execute(self, request: Any = None) -> MealList:
        return self.get_meal_list_use_case.execute()