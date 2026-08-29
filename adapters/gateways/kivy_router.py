from logging import getLogger

from adapters.controllers.dtos.time_view_model import TimeList
from usecases.dtos.meal_list import MealList
from adapters.controllers.dtos.card_view_model import CardViewModel
from adapters.controllers.dtos.matrix_data_view_model import MatrixDataViewModel

logger = getLogger(__name__)

class KivyRouter:
    """
    Classe que roteia requests do kivy para os controllers corretos.
    """
    def __init__(self, time_controller,
                date_hour_matrix_controller,
                meal_controller,
                save_request_controller,
                delete_card_controller
                ):
        self.time_controller = time_controller
        self.date_hour_matrix_controller = date_hour_matrix_controller
        self.meal_controller = meal_controller
        self.save_request_controller = save_request_controller
        self.delete_card_controller = delete_card_controller


    def get_meal_list(self) -> MealList:
        return self.meal_controller.get_meal_list()


    def get_time_list(self) -> TimeList:
        logger.debug("Getting time list...")
        return self.time_controller.get_time_list()
    

    def save_card(self, data) -> None:
        logger.debug(f"Saving card: {data}")
        return self.save_request_controller.save_card(data)
    

    def get_hour_date_matrix_data(self) -> MatrixDataViewModel:
        logger.debug(f"Getting data for matrix")
        return self.date_hour_matrix_controller.get_data()
    

    def delete_card(self, data) -> None:
        logger.debug(f"Routing to card deletion...")
        return self.delete_card_controller.delete_card(data)
