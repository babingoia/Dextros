from logging import getLogger
from typing import Any
from adapters.controllers.i_controller import IController
from adapters.controllers.dtos.single_row_matrix_view import SingleRowMatrixView
from adapters.controllers.mappers.mappers import single_row_to_view_model

logger = getLogger(__name__)

class AverageGlycemiaDayMatrixController(IController[Any, SingleRowMatrixView]):
    """
    """
    def __init__(self, get_average_glycemia_day_use_case):
        self.get_average_glycemia_day_use_case = get_average_glycemia_day_use_case


    def execute(self, request: Any = None) -> SingleRowMatrixView:
        data = self.get_average_glycemia_day_use_case.execute()
        data_view_model = single_row_to_view_model(data)
        return data_view_model