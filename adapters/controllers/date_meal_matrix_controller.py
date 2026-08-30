from logging import getLogger
from typing import Any

from adapters.controllers.dtos.matrix_data_view_model import MatrixDataViewModel
from adapters.controllers.i_controller import IController
from adapters.controllers.mappers.mappers import matrix_to_view_model


logger = getLogger(__name__)


class DateMealMatrixController(IController[Any, MatrixDataViewModel]):
    """Request que retorna os dados para compor uma matrix 2D de glicemia por data x refeição."""
    def __init__(self, get_meal_date_matrix_use_case):
        self.get_meal_date_matrix_use_case = get_meal_date_matrix_use_case


    def execute(self, request: Any = None) -> MatrixDataViewModel:
        matrix_data = self.get_meal_date_matrix_use_case.execute()
        matrix_view_model = matrix_to_view_model(matrix_data)
        return matrix_view_model
