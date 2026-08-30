# usecases/dtos/single_row_graph_data.py

from dataclasses import dataclass
from usecases.dtos.card_output import CardOutput


@dataclass
class SingleRowMatrixData:
    """
    Estrutura para gráficos 1D / single row.
    """

    col_headers: list[str]
    cells: list[CardOutput | None]