from dataclasses import dataclass
from adapters.controllers.dtos.card_average_view_model import CardAverageViewModel

@dataclass
class SingleRowMatrixView:
    """
    DTO para gráfico unidimensional.

    As células são valores simples de gráfico.
    """

    col_headers: list[str]
    cells: list[CardAverageViewModel]