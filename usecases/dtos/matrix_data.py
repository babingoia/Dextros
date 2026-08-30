from dataclasses import dataclass
from usecases.dtos.card_output import CardOutput

@dataclass
class MatrixData:
    """
    Estrutura de dados que representa uma matrix 2D. Por isso não recebe dados tipados.
    """
    row_headers: list[str]
    col_headers: list[str]
    cell_data: dict[tuple[int, int], CardOutput]