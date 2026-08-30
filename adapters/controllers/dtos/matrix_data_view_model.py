from dataclasses import dataclass
from adapters.controllers.dtos.card_view_model import CardViewModel

@dataclass
class MatrixDataViewModel:
    """Estrutura que representa uma matrix 2D para a UI."""
    row_headers: list[str]
    col_headers: list[str]
    cell_data: dict[tuple[int, int], CardViewModel] 