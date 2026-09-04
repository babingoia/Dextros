# usecases/dtos/single_row_matrix_data.py

from dataclasses import dataclass

from usecases.dtos.card_average_output import CardAverageOutput


@dataclass
class SingleRowMatrixData:
    """
    DTO para gráfico unidimensional.

    As células são valores agregados representados por CardAverageOutput.
    """

    col_headers: list[str]
    cells: list[CardAverageOutput]