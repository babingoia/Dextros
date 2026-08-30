# usecases/dtos/single_row_graph_data.py

from dataclasses import dataclass


@dataclass
class SingleRowMatrixData:
    """
    DTO para gráfico unidimensional.

    As células são valores simples de gráfico.
    """

    col_headers: list[str]
    cells: list[str | None]