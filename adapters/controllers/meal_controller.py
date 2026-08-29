from usecases.dtos.meal_list import MealList

class MealController:
    def __init__(self, get_meal_list_use_case):
        self.get_meal_list_use_case = get_meal_list_use_case


    def get_meal_list(self) -> MealList:
        return self.get_meal_list_use_case.execute()    