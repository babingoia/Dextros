from logging import getLogger

from adapters.controllers.dtos.matrix_data_view_model import MatrixDataViewModel
from adapters.controllers.mappers.mappers import matrix_to_view_model


logger = getLogger(__name__)


class DateHourMatrixController:
    def __init__(self, get_hour_date_matrix_use_case):
        self.get_hour_date_matrix_use_case = get_hour_date_matrix_use_case


    def get_data(self) -> MatrixDataViewModel:
        matrix_data = self.get_hour_date_matrix_use_case.execute()
        matrix_view_model = matrix_to_view_model(matrix_data)
        logger.debug(f"matrix_view_model got: {matrix_view_model.row_headers}")
        logger.debug(f"matrix_view_model got: {matrix_view_model.col_headers}")
        logger.debug(f"matrix_view_model got: {matrix_view_model.cell_data}")
        return matrix_view_model
